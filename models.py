from pydantic import BaseModel
from typing import List, Dict, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    role: str
    school_id: Optional[str] = None

# This is the missing model needed for user registration
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "student"  # A default role can be helpful

class UserInDB(User):
    hashed_password: str

class ChatMessage(BaseModel):
    role: str
    content: str

class RAGScope(BaseModel):
    scope_type: str
    scope_id: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    persona: str
    educational_level: str
    llm_provider: str
    rag_scope: Optional[RAGScope] = None

class ChatResponse(BaseModel):
    role: str
    content: str

class UploadResponse(BaseModel):
    message: str
    doc_id: str # Added doc_id as it was in the main.py upload endpoint

class AssignmentRequest(BaseModel):
    title: str
    description: str
    due_date: Optional[str] = None

class AssignmentResponse(AssignmentRequest):
    id: str

class SubmissionRequest(BaseModel):
    assignment_id: str
    content: str

class GradeResponse(BaseModel):
    grade: int
    feedback: str

class SchoolRequest(BaseModel):
    name: str

class SchoolResponse(BaseModel):
    school_id: str
    invite_code: str

class JoinSchoolRequest(BaseModel):
    invite_code: str

class JoinClassroomRequest(BaseModel):
    join_code: str

class ClassroomDetailsResponse(BaseModel):
    student_ids: List[str]
    pending_student_ids: List[str]
    join_code: str

class DocumentResponse(BaseModel):
    id: str
    filename: str
    category: str

class AttendanceRequest(BaseModel):
    date: str
    present_students: List[str]
