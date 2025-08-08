import streamlit as st
import requests
from dotenv import load_dotenv
import os

from collections import defaultdict
import datetime

# Local Imports
from llm_config import LLM_PROVIDERS

# Load environment variables from .env file
load_dotenv()

# --- Page Configuration & API Helper ---
st.set_page_config(page_title="Educational AI Platform", page_icon="🎓", layout="wide")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def api_request(method: str, endpoint: str, data: dict = None, files: dict = None):
    try:
        url = f"{API_BASE_URL}/{endpoint}"

        headers = {}
        if "access_token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"

        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, files=files, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, files=files, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None

        if response.status_code == 401:
            st.error("Authentication failed. Please log in again.")
            if "access_token" in st.session_state:
                del st.session_state["access_token"]
            st.rerun()
            return None

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

# --- UI Components ---

def draw_login_screen():
    st.title("Welcome to the Educational AI Platform 🎓")
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted and username and password:
                with st.spinner("Authenticating..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/token",
                            data={"username": username, "password": password}
                        )
                        if response.ok:
                            st.session_state.access_token = response.json()["access_token"]
                            # Get user details after login
                            user_details = api_request("GET", "users/me")
                            if user_details:
                                st.session_state.username = user_details["username"]
                                st.session_state.role = user_details["role"]
                                st.rerun()
                        else:
                            st.error("Login failed. Please check your credentials.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to connect to the backend: {e}")

    with register_tab:
        with st.form("register_form"):
            username = st.text_input("New Username")
            password = st.text_input("New Password", type="password")
            role = st.selectbox("Choose your role:", ["Student", "Educator", "School Admin"])
            submitted = st.form_submit_button("Register")
            if submitted and username and password:
                payload = {"username": username, "password": password, "role": role}
                response = api_request("POST", "register", data=payload)
                if response:
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Registration failed.")

def draw_rag_ui():
    st.header("🧠 Knowledge Base (RAG)")
    # --- RAG UI for uploading files and managing knowledge base ---
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"], key="rag_uploader")
    category = st.text_input("Document Category (e.g., 'Physics', 'History')", key="doc_category")

    if uploaded_file and category:
        if st.button("Upload & Process Document"):
            with st.spinner("Uploading and processing..."):
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = api_request("POST", f"documents?category={category}", files=files)
                if response:
                    st.success(f"Document '{uploaded_file.name}' processed successfully!")
                    st.session_state.doc_id = response.get("doc_id")
                else:
                    st.error("Failed to upload document.")
    
    st.subheader("Your Documents")
    docs_response = api_request("GET", "documents")
    if docs_response:
        docs = docs_response
        selected_doc_id = st.selectbox(
            "Select a document to use for RAG:",
            options=[d['id'] for d in docs],
            format_func=lambda x: next((d['filename'] for d in docs if d['id'] == x), x),
            key="rag_doc_selector"
        )
        if selected_doc_id:
            st.session_state.rag_scope = {"scope_type": "document", "scope_id": selected_doc_id}
            st.info(f"Using document: **{selected_doc_id}** for RAG.")
        else:
            st.session_state.rag_scope = None
    else:
        st.info("No documents uploaded yet.")

def draw_storage_usage_ui():
    st.subheader("📦 Storage Usage")
    usage_response = api_request("GET", "storage-usage")
    if usage_response:
        usage = usage_response.get("usage_mb", 0)
        limit = usage_response.get("limit_mb", 100)
        st.metric("Used Space", f"{usage:.2f} MB", f"of {limit:.2f} MB")
        st.progress(usage / limit)

def draw_chat_interface():
    st.subheader("AI Tutor Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to learn about?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                payload = {
                    "messages": st.session_state.messages,
                    "persona": st.session_state.get("ai_persona", "You are a helpful expert."),
                    "educational_level": st.session_state.get("educational_level", ""),
                    "llm_provider": st.session_state.get("llm_provider", "TogetherAI"),
                    "rag_scope": st.session_state.get("rag_scope")
                }
                response_data = api_request("POST", "chat", data=payload)
                if response_data:
                    ai_response = response_data.get("content")
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.session_state.messages.pop()
                    st.error("Failed to get response from the backend.")

def draw_educator_ui():
    st.header(f"Educator Dashboard: {st.session_state.username}")
    tabs = st.tabs(["Classroom", "Assignments", "Attendance", "AI Tutor Chat"])
    with tabs[0]: # Classroom Management
        st.subheader("Classroom Management")
        # TODO: Add logic for managing students and join codes
        st.info("Classroom management features coming soon!")
    with tabs[1]: # Assignment Management
        st.subheader("Assignment Management")
        # TODO: Add logic for creating and viewing assignments
        st.info("Assignment management features coming soon!")
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

def draw_attendance_ui():
    st.subheader("Mark Attendance")
    # TODO: Add attendance marking functionality
    st.info("Attendance features coming soon!")

# --- Main App Dispatcher ---
if "access_token" not in st.session_state:
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
