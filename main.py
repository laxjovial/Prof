
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import tempfile
from dotenv import load_dotenv
import uuid

# Local Imports
import database, ai, rag

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List
import os
import tempfile
from dotenv import load_dotenv

# Langchain Imports
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_together import TogetherEmbeddings
from together import Together

# Local Imports
import database
import ai
import rag


# Load environment variables
load_dotenv()


app = FastAPI(title="Educational AI Platform API")

# --- Pydantic Models ---
class RAGScope(BaseModel):
    scope_type: str  # e.g., "document", "category"
    scope_id: str    # e.g., a document_id or a category_name
class ChatRequest(BaseModel):
    messages: List[Dict]
    persona: str
    educational_level: str
    llm_provider: str
    rag_scope: Optional[RAGScope] = None
# ... (other models are fine)
class SchoolRequest(BaseModel): name: str
class SchoolResponse(BaseModel): school_id: str; invite_code: str
class JoinSchoolRequest(BaseModel): invite_code: str
class JoinClassroomRequest(BaseModel): join_code: str
class ClassroomDetailsResponse(BaseModel): student_ids: List[str]; pending_student_ids: List[str]; join_code: str
class ChatResponse(BaseModel): role: str; content: str
class UploadResponse(BaseModel): message: str; doc_id: str
class AssignmentRequest(BaseModel): title: str; description: str; due_date: Optional[str] = None
class AssignmentResponse(BaseModel): id: str; title: str; description: str; due_date: Optional[str] = None
class DocumentResponse(BaseModel): id: str; filename: str; category: str
class AttendanceRequest(BaseModel): date: str; present_students: List[str]
class SubmissionRequest(BaseModel):
    assignment_id: str
    content: str
class GradeResponse(BaseModel):
    grade: int
    feedback: str

# --- Dependencies & State ---
def get_current_user(x_username: str = Header(...)):
    if not x_username: raise HTTPException(status_code=401, detail="Username header missing")
    return x_username
def get_db(): return app.state.db
def get_current_educator(current_user: str = Depends(get_current_user), db: firestore.Client = Depends(get_db)):
    # ... (logic unchanged)
    return current_user
@app.on_event("startup")
async def startup_event():
    # ... (logic unchanged)
    app.state.storage_limit_mb = float(os.getenv("USER_STORAGE_LIMIT_MB", 100.0))
    print("FastAPI server started successfully.")

# --- Endpoints ---
@app.post("/documents", response_model=UploadResponse)
async def upload_document_endpoint(category: str = Form(...), file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    # Check storage limit
    current_usage_mb = rag.get_user_storage_usage_mb(app.state.gcs_bucket_name, current_user)
    file_size_mb = file.size / (1024 * 1024)

    if current_usage_mb + file_size_mb > app.state.storage_limit_mb:
        raise HTTPException(
            status_code=413,
            detail=f"Upload would exceed your storage limit of {app.state.storage_limit_mb} MB."
        )

    doc_id = str(uuid.uuid4())
    gcs_path = f"vector_stores/{current_user}/{doc_id}"
    # ... (file processing and saving to GCS logic) ...
    database.add_document_metadata(app.state.db, current_user, gcs_path, category, file.filename)
    return {"message": "Document processed and saved.", "doc_id": doc_id}

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents_endpoint(current_user: str = Depends(get_current_user)):
    docs = database.get_documents_for_user(app.state.db, current_user)
    return docs

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: str = Depends(get_current_user)):
    vector_store = None
    if request.rag_scope:
        # This is a simplified logic. A real implementation would handle category-wide search.
        gcs_path_prefix = f"vector_stores/{current_user}/{request.rag_scope.scope_id}"
        vector_store = rag.load_vector_store_from_gcs(app.state.gcs_bucket_name, gcs_path_prefix, app.state.embeddings)

    ai_response = ai.get_ai_response(
        provider=request.llm_provider,
        system_prompt=f"{request.persona} at {request.educational_level} level",
        messages=request.messages,
        vector_store=vector_store,
        use_rag=bool(request.rag_scope)
    )
    if "An error occurred" in ai_response:
        raise HTTPException(status_code=500, detail=ai_response)
    return ChatResponse(role="assistant", content=ai_response)

@app.get("/assignments/educator", response_model=List[AssignmentResponse])
async def get_educator_assignments_endpoint(educator: str = Depends(get_current_educator)):
    """Endpoint for an educator to get their list of created assignments."""
    assignments = database.get_assignments_for_educator(app.state.db, educator)
    return assignments

@app.get("/storage-usage", response_model=Dict[str, float])
async def get_storage_usage_endpoint(current_user: str = Depends(get_current_user)):
    """Endpoint for a user to check their current storage usage."""
    usage_mb = rag.get_user_storage_usage_mb(app.state.gcs_bucket_name, current_user)
    return {"usage_mb": usage_mb, "limit_mb": app.state.storage_limit_mb}

@app.post("/attendance")
async def mark_attendance_endpoint(request: AttendanceRequest, educator: str = Depends(get_current_educator)):
    """Endpoint for an educator to mark attendance for a specific date."""
    database.mark_attendance(app.state.db, educator, request.date, request.present_students)
    return {"message": f"Attendance for {request.date} recorded successfully."}

@app.post("/submissions/grade", response_model=GradeResponse)
async def grade_submission_endpoint(request: SubmissionRequest, current_user: str = Depends(get_current_user)):
    """Grades a student's submission for an assignment."""
    # 1. Get the original assignment
    assignment = database.get_assignment(app.state.db, request.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    # 2. Construct a detailed prompt for the AI grading
    grading_prompt = f"""
    You are an expert teaching assistant. Your task is to grade a student's submission.
    Provide a numerical score out of 100 and constructive feedback.
    Return your response as a JSON object with two keys: "grade" (an integer) and "feedback" (a string).

    Original Assignment Description:
    ---
    {assignment['description']}
    ---

    Student's Submission:
    ---
    {request.content}
    ---
    """

    # 3. Call the AI with the grading prompt
    # We use a generic persona for the grading task
    ai_response_str = ai.get_ai_response(
        provider="TogetherAI", # Or make this configurable
        system_prompt="You are a fair and helpful grading assistant who provides clear, actionable feedback. You always respond in JSON format.",
        messages=[{"role": "user", "content": grading_prompt}],
        use_rag=False # RAG is not needed for this task
    )

    # 4. Parse the JSON response from the AI
    try:
        grade_data = json.loads(ai_response_str)
        grade = int(grade_data.get("grade", 0))
        feedback = grade_data.get("feedback", "No feedback provided.")
    except (json.JSONDecodeError, TypeError, ValueError):
        raise HTTPException(status_code=500, detail="AI returned an invalid format for the grade.")

    # 5. Save the submission and grade to the database
    database.save_submission(app.state.db, request.assignment_id, current_user, request.content, grade, feedback)

    return GradeResponse(grade=grade, feedback=feedback)

# ... (other endpoints for classroom, assignments etc. remain)
# ...

app = FastAPI(
    title="Educational AI Platform API",
    description="API for providing AI-powered educational content and chat.",
    version="1.0.0",
)

# --- Pydantic Models ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    username: str
    messages: List[ChatMessage]
    persona: str
    educational_level: str
    use_rag: bool

class ChatResponse(BaseModel):
    role: str
    content: str

class UploadResponse(BaseModel):
    message: str
    doc_id: str

# --- App State and Startup Event ---
@app.on_event("startup")
async def startup_event():
    """On startup, initialize the AI clients."""
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise RuntimeError("TOGETHER_API_KEY not found in environment variables.")

    app.state.ai_client = Together(api_key=api_key)
    app.state.embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval", api_key=api_key)
    app.state.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not app.state.gcs_bucket_name:
        raise RuntimeError("GCS_BUCKET_NAME not found in environment variables.")
    print("FastAPI server started successfully.")

# --- API Endpoints ---
@app.post("/upload-document/{username}", response_model=UploadResponse)
async def upload_document(username: str, file: UploadFile = File(...)):
    """Handles file uploads, processes them, and saves the vector store to GCS."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        loader = PyPDFLoader(tmp_file_path) if file.content_type == "application/pdf" else TextLoader(tmp_file_path)
        docs = loader.load()
        vector_store = rag.create_vector_store(docs, app.state.embeddings)

        # The "doc_id" for the GCS path will be the username for simplicity
        destination_blob_prefix = f"vector_stores/{username}"
        success = rag.save_vector_store_to_gcs(vector_store, app.state.gcs_bucket_name, destination_blob_prefix)
        os.remove(tmp_file_path)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save vector store to GCS.")

        return {"message": "Document processed and saved successfully", "doc_id": username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint. Handles user messages and generates AI responses."""
    system_prompt = f"{request.persona} You are teaching at a {request.educational_level} level." if request.educational_level else request.persona

    vector_store = None
    if request.use_rag:
        # Load vector store from GCS for this user
        source_blob_prefix = f"vector_stores/{request.username}"
        vector_store = rag.load_vector_store_from_gcs(app.state.gcs_bucket_name, source_blob_prefix, app.state.embeddings)

    messages_dict = [msg.dict() for msg in request.messages]

    ai_response_content = ai.get_ai_response(
        client=app.state.ai_client,
        system_prompt=system_prompt,
        messages=messages_dict,
        vector_store=vector_store,
        use_rag=request.use_rag
    )

    if ai_response_content is None:
        raise HTTPException(status_code=500, detail="Failed to get response from AI.")

    return ChatResponse(role="assistant", content=ai_response_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

