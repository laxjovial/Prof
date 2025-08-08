from google.cloud import firestore
import json
import uuid
from typing import Dict, List, Optional
import auth

# --- Firestore Initialization ---
def init_firestore():
    return firestore.Client()

# --- User & School Management ---
def get_user(db: firestore.Client, username: str) -> Optional[Dict]:
    """Retrieves a user document by username."""
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None

def get_or_create_user(db: firestore.Client, username: str, role: str, password: str = "password") -> Dict:
    """Gets a user document, or creates it with a default password if it doesn't exist."""
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    else:
        hashed_password = auth.get_password_hash(password)
        user_data = {"role": role, "school_id": None, "hashed_password": hashed_password}
        user_ref.set(user_data)
        if role == "Educator":
            db.collection("classrooms").document(username).set({
                "student_ids": [],
                "pending_student_ids": [],
                "join_code": str(uuid.uuid4())
            })
        return user_data

def create_school(db: firestore.Client, school_name: str) -> Dict:
    # ... (code is correct)
    pass

def join_school(db: firestore.Client, educator_username: str, invite_code: str) -> Optional[str]:
    # ... (code is correct)
    pass

# --- Classroom Management ---
def get_classroom_details(db: firestore.Client, educator_username: str) -> Optional[Dict]:
    # ... (code is correct)
    pass

def request_to_join_classroom(db: firestore.Client, student_username: str, join_code: str) -> bool:
    # ... (code is correct)
    pass

def approve_student_join_request(db: firestore.Client, educator_username: str, student_username: str):
    # ... (code is correct)
    pass

# --- RAG Document Management ---
def add_document_metadata(db: firestore.Client, owner_id: str, gcs_path: str, category: str, filename: str, doc_id: str):
    doc_data = {"owner_id": owner_id, "gcs_path": gcs_path, "category": category, "filename": filename}
    db.collection("documents").document(doc_id).set(doc_data)

def get_documents_for_user(db: firestore.Client, owner_id: str) -> List[Dict]:
    docs_query = db.collection("documents").where("owner_id", "==", owner_id).stream()
    documents = []
    for doc in docs_query:
        doc_data = doc.to_dict()
        doc_data["id"] = doc.id
        documents.append(doc_data)
    return documents

# --- Assignment & Attendance ---
def create_assignment(db: firestore.Client, educator_id: str, title: str, description: str, due_date) -> str:
    """Creates a new assignment, gets its ID, and then assigns it to the class."""
    assignment_data = {"educator_id": educator_id, "title": title, "description": description, "due_date": due_date}
    _, assignment_ref = db.collection("assignments").add(assignment_data)
    assign_to_class(db, educator_id, assignment_ref.id) # Assign to current students
    return assignment_ref.id

def get_assignments_for_educator(db: firestore.Client, educator_id: str) -> List[Dict]:
    assignments_query = db.collection("assignments").where("educator_id", "==", educator_id).stream()
    assignments = []
    for assignment in assignments_query:
        assignment_data = assignment.to_dict()
        assignment_data["id"] = assignment.id
        assignments.append(assignment_data)
    return assignments

def assign_to_class(db: firestore.Client, educator_id: str, assignment_id: str):
    """Assigns an assignment to all students in an educator's class."""
    students = get_students_for_educator(db, educator_id)
    for student_id in students:
        db.collection("student_assignments").add({
            "student_id": student_id,
            "assignment_id": assignment_id,
            "status": "assigned"
        })

def get_assignments_for_student(db: firestore.Client, student_username: str) -> List[Dict]:
    """Retrieves all assignments for a student via the mapping collection."""
    student_assignments_query = db.collection("student_assignments").where("student_id", "==", student_username).stream()
    assignment_ids = [doc.to_dict()['assignment_id'] for doc in student_assignments_query]

    if not assignment_ids:
        return []

    assignments = []
    for assignment_id in assignment_ids:
        assignment = get_assignment(db, assignment_id)
        if assignment:
            assignments.append(assignment)
    return assignments

def get_assignment(db: firestore.Client, assignment_id: str) -> Optional[Dict]:
    """Retrieves a single assignment by its ID."""
    assignment_ref = db.collection("assignments").document(assignment_id)
    doc = assignment_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def save_submission(db: firestore.Client, assignment_id: str, student_id: str, content: str, grade: int, feedback: str):
    """Saves a student's submission, grade, and feedback."""
    submission_data = {
        "assignment_id": assignment_id,
        "student_id": student_id,
        "content": content,
        "grade": grade,
        "feedback": feedback,
        "submitted_at": firestore.SERVER_TIMESTAMP
    }
    db.collection("submissions").add(submission_data)

def mark_attendance(db: firestore.Client, educator_id: str, date_str: str, present_students: List[str]):
    # ... (code is correct)
    pass

def load_chat_history(db: firestore.Client, username: str):
    """
    Loads chat history for a given user from Firestore.
    """
    doc_ref = db.collection("chat_histories").document(username)
    doc = doc_ref.get()
    return doc.to_dict().get("messages", []) if doc.exists else []

def save_chat_history(db: firestore.Client, username: str, messages: list):
    """
    Saves chat history for a given user to Firestore.
    """
    doc_ref = db.collection("chat_histories").document(username)
    doc_ref.set({"messages": messages})
