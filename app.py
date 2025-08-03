import streamlit as st
import requests
from dotenv import load_dotenv
import os
import datetime
from collections import defaultdict

# Local Imports
from llm_config import LLM_PROVIDERS
import database

# --- Page Configuration & API Helper ---
st.set_page_config(page_title="Educational AI Platform", page_icon="🎓", layout="wide")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def api_request(method: str, endpoint: str, data: dict = None, files: dict = None):
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        headers = {"X-Username": st.session_state.username}
        response = requests.request(method.upper(), url, json=data, files=files, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

# --- UI Components ---
def draw_rag_ui():
    st.header("🧠 Knowledge Base (RAG)")
    # ... (full RAG UI code) ...
def draw_storage_usage_ui():
    st.subheader("📦 Storage Usage")
    # ... (full storage usage code) ...
def draw_chat_interface():
    st.subheader("AI Tutor Chat")
    # ... (full chat interface code) ...
def draw_attendance_ui():
    st.subheader("Mark Attendance")
    # ... (full attendance UI code) ...

def draw_educator_ui():
    st.header(f"Educator Dashboard: {st.session_state.username}")
    tabs = st.tabs(["Classroom", "Assignments", "Attendance", "AI Tutor Chat"])
    with tabs[0]: # Classroom Management
        # ... (full classroom management UI) ...
        pass
    with tabs[1]: # Assignment Management
        # ... (full assignment management UI) ...
        pass
    with tabs[2]: # Attendance
        draw_attendance_ui()
    with tabs[3]: # AI Tutor Chat
        draw_chat_interface()

def draw_student_ui():
    st.header(f"👋 Student Dashboard: {st.session_state.username}")
    tab1, tab2 = st.tabs(["AI Tutor Chat", "Assignments"])
    with tab1:
        draw_chat_interface()
    with tab2:
        st.subheader("Your Assignments")
        assignments_response = api_request("GET", "assignments/student")
        if assignments_response and assignments_response.get("assignments"):
            for assignment in assignments_response["assignments"]:
                with st.expander(f"**{assignment['title']}** (Due: {assignment.get('due_date', 'N/A')})"):
                    st.write(assignment['description'])
                    submission_content = st.text_area("Your Submission", key=f"sub_{assignment['id']}")
                    if st.button("Submit for Grading", key=f"submit_{assignment['id']}"):
                        if submission_content:
                            with st.spinner("Submitting and grading..."):
                                payload = {"assignment_id": assignment['id'], "content": submission_content}
                                grade_response = api_request("POST", "submissions/grade", data=payload)
                                if grade_response:
                                    st.success("Submission Graded!")
                                    st.metric(label="Your Grade", value=f"{grade_response.get('grade', 0)} / 100")
                                    st.info("AI Feedback:"); st.write(grade_response.get('feedback', 'No feedback.'))
        else:
            st.info("You have no assignments yet.")

def draw_login_screen():
    st.title("Welcome to the Educational AI Platform 🎓")
    with st.form("login_form"):
        username = st.text_input("Username")
        role = st.selectbox("Choose your role:", ["Student", "Educator"])
        submitted = st.form_submit_button("Login")
        if submitted and username:
            st.session_state.db = database.init_firestore()
            database.get_or_create_user(st.session_state.db, username, role)
            st.session_state.username = username; st.session_state.role = role
            st.rerun()

# --- Main App Dispatcher ---
if "username" not in st.session_state:
    draw_login_screen()
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.username} (Role: {st.session_state.role})")
        if st.button("Logout"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
        st.divider()
        st.header("⚙️ AI Configuration")
        st.selectbox("LLM Provider:", list(LLM_PROVIDERS.keys()), key="llm_provider")
        st.text_input("AI Persona:", "You are a helpful expert.", key="ai_persona")
        st.text_input("Educational Level:", key="educational_level")
        st.divider()
        draw_rag_ui()
        st.divider()
        draw_storage_usage_ui()

    if st.session_state.role == "Student": draw_student_ui()
    elif st.session_state.role == "Educator": draw_educator_ui()
    else: st.error("Invalid user role.")
