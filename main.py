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
