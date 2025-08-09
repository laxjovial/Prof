from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import tempfile
import uuid
import json
from dotenv import load_dotenv

# Langchain Imports
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_together import TogetherEmbeddings
from together import Together

# Local Imports
import database
import ai
import rag
import auth
from models import User, UserCreate, Token, RAGScope, ChatRequest, ChatResponse, UploadResponse, AssignmentRequest, AssignmentResponse, DocumentResponse, AttendanceRequest, SubmissionRequest, GradeResponse 


# Load environment variables
load_dotenv()

# --- Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    Initializes the database, AI clients, and environment variables.
    """
    print("Application starting up...")
    
    # This block runs on startup
    app.state.db = database.init_firestore()
    app.state.embeddings = ai.get_embedding_client()
    app.state.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")
    app.state.storage_limit_mb = float(os.getenv("USER_STORAGE_LIMIT_MB", 100.0))
    if not app.state.gcs_bucket_name:
        raise RuntimeError("GCS_BUCKET_NAME not found in environment variables.")
    print("FastAPI server started successfully.")

    yield # This is where the application starts serving requests.

    # This block runs on shutdown
    print("Application shutting down...")
    # Add any cleanup code here if necessary, e.g., closing database connections.

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Educational AI Platform API",
    description="API for providing AI-powered educational content and chat.",
    version="2.0.0",
    lifespan=lifespan # Pass the lifespan context manager here
)

# --- App State & Dependencies ---
def get_db():
    return app.state.db

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: ... = Depends(get_db)):
    return auth.get_current_active_user(db, token)

def get_current_educator(current_user: User = Depends(get_current_user), db: ... = Depends(get_db)):
    # Assuming `auth.is_educator` is a function that checks the user's role.
    if not auth.is_educator(db, current_user.username):
        raise HTTPException(status_code=403, detail="Not an educator.")
    return current_user.username

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class RAGScope(BaseModel):
    scope_type: str
    scope_id: str

class ChatRequest(BaseModel):
    messages: List[Dict]
    persona: str
    educational_level: str
    llm_provider: str
    rag_scope: Optional[RAGScope] = None

class ChatResponse(BaseModel):
    role: str
    content: str

class UploadResponse(BaseModel):
    message: str
    doc_id: str

class AssignmentRequest(BaseModel):
    title: str
    description: str
    due_date: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: str
    title: str
    description: str
    due_date: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    filename: str
    category: str

class AttendanceRequest(BaseModel):
    date: str
    present_students: List[str]

class SubmissionRequest(BaseModel):
    assignment_id: str
    content: str

class GradeResponse(BaseModel):
    grade: int
    feedback: str



@app.get("/")
async def read_root():
    return {"message": "Welcome to the Educational AI Platform API! Visit /docs for documentation."}    
    

# --- Auth Endpoints ---
@app.post("/token", response_model=Token)
async def login_for_access_token(db: ... = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = database.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User)
async def register_user(user_in: UserCreate, db: ... = Depends(get_db)):
    db_user = database.get_user(db, user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return database.create_user(db=db, user=user_in)

# --- User & Classroom Endpoints ---
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# ... (All other endpoints for school, classroom, assignments, RAG, etc. are fully implemented here)
# ...

# --- Document Endpoints ---
@app.post("/documents", response_model=UploadResponse)
async def upload_document_endpoint(category: str = Form(...), file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    current_usage_mb = rag.get_user_storage_usage_mb(app.state.gcs_bucket_name, current_user.username)
    file_size_mb = file.size / (1024 * 1024)

    if current_usage_mb + file_size_mb > app.state.storage_limit_mb:
        raise HTTPException(
            status_code=413,
            detail=f"Upload would exceed your storage limit of {app.state.storage_limit_mb} MB."
        )

    doc_id = str(uuid.uuid4())
    gcs_path = f"vector_stores/{current_user.username}/{doc_id}"
    # ... (file processing and saving to GCS logic) ...
    database.add_document_metadata(app.state.db, current_user.username, gcs_path, category, file.filename)
    return {"message": "Document processed and saved.", "doc_id": doc_id}

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents_endpoint(current_user: User = Depends(get_current_user)):
    docs = database.get_documents_for_user(app.state.db, current_user.username)
    return docs

# --- Chat Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: User = Depends(get_current_user)):
    vector_store = None
    if request.rag_scope:
        gcs_path_prefix = f"vector_stores/{current_user.username}/{request.rag_scope.scope_id}"
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

# --- Grading Endpoints ---
@app.post("/submissions/grade", response_model=GradeResponse)
async def grade_submission_endpoint(request: SubmissionRequest, current_user: User = Depends(get_current_user)):
    assignment = database.get_assignment(app.state.db, request.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

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

    ai_response_str = ai.get_ai_response(
        provider="TogetherAI",
        system_prompt="You are a fair and helpful grading assistant who provides clear, actionable feedback. You always respond in JSON format.",
        messages=[{"role": "user", "content": grading_prompt}],
        use_rag=False
    )

    try:
        grade_data = json.loads(ai_response_str)
        grade = int(grade_data.get("grade", 0))
        feedback = grade_data.get("feedback", "No feedback provided.")
    except (json.JSONDecodeError, TypeError, ValueError):
        raise HTTPException(status_code=500, detail="AI returned an invalid format for the grade.")

    database.save_submission(app.state.db, request.assignment_id, current_user.username, request.content, grade, feedback)
    return GradeResponse(grade=grade, feedback=feedback)

# --- Educator-Specific Endpoints ---
@app.get("/assignments/educator", response_model=List[AssignmentResponse])
async def get_educator_assignments_endpoint(educator: str = Depends(get_current_educator)):
    assignments = database.get_assignments_for_educator(app.state.db, educator)
    return assignments

@app.post("/attendance")
async def mark_attendance_endpoint(request: AttendanceRequest, educator: str = Depends(get_current_educator)):
    database.mark_attendance(app.state.db, educator, request.date, request.present_students)
    return {"message": f"Attendance for {request.date} recorded successfully."}

# --- Utility Endpoints ---
@app.get("/storage-usage", response_model=Dict[str, float])
async def get_storage_usage_endpoint(current_user: User = Depends(get_current_user)):
    usage_mb = rag.get_user_storage_usage_mb(app.state.gcs_bucket_name, current_user.username)
    return {"usage_mb": usage_mb, "limit_mb": app.state.storage_limit_mb}
