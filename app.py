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
        url = f"{API_BAE_URL}/{endpoint}"
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
    with st.form("upload_form", clear_on_submit=True):
        category = st.text_input("Document Category", "General")
        uploaded_file = st.file_uploader("Upload a document", type=['pdf', 'txt'])
        submitted = st.form_submit_button("Upload and Process")
        if submitted and uploaded_file:
            with st.spinner("Processing document..."):
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = api_request("POST", "documents", data={"category": category}, files=files)
                if response: st.success("Document uploaded successfully!")
                else: st.error("File upload failed.")

    st.divider()
    st.write("**Document Library & Context Selection**")
    docs = api_request("GET", "documents")
    if docs:
        categories = defaultdict(list)
        for doc in docs: categories[doc['category']].append(doc)

        options = {"None": None}
        for category, doc_list in categories.items():
            options[f"Category: {category}"] = {"scope_type": "category", "scope_id": category}
            for doc in doc_list: options[f"  - {doc['filename']}"] = {"scope_type": "document", "scope_id": doc['id']}

        selected_key = st.selectbox("Choose context for your chat:", options.keys())
        st.session_state.rag_scope = options[selected_key]
    else:
        st.info("No documents uploaded yet.")

def draw_storage_usage_ui():
    st.subheader("📦 Storage Usage")
    response = api_request("GET", "storage-usage")
    if response:
        usage_mb = response.get("usage_mb", 0)
        limit_mb = response.get("limit_mb", 100)
        st.progress(usage_mb / limit_mb if limit_mb > 0 else 0)
        st.write(f"{usage_mb:.2f} / {limit_mb:.2f} MB used")

def draw_chat_interface():
    st.subheader("AI Tutor Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = database.load_chat_history(st.session_state.db, st.session_state.username)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask your AI tutor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                payload = {
                    "messages": st.session_state.messages,
                    "persona": st.session_state.ai_persona,
                    "educational_level": st.session_state.educational_level,
                    "llm_provider": st.session_state.llm_provider,
                    "rag_scope": st.session_state.get("rag_scope")
                }
                response = api_request("POST", "chat", data=payload)
                if response:
                    content = response.get("content", "Error: No content in response.")
                    st.markdown(content)
                    st.session_state.messages.append({"role": "assistant", "content": content})
                    database.save_chat_history(st.session_state.db, st.session_state.username, st.session_state.messages)
                else:
                    st.session_state.messages.pop()

def draw_attendance_ui():
    st.subheader("Mark Attendance")
    response = api_request("GET", "classroom")
    if not response or not response.get("student_ids"):
        st.warning("You have no students in your classroom.")
        return
    students = response["student_ids"]

    attendance_date = st.date_input("Select Date", datetime.date.today())
    present_students = [s for s in students if st.checkbox(s, key=f"att_{s}")]

    if st.button("Submit Attendance"):
        payload = {"date": str(attendance_date), "present_students": present_students}
        response = api_request("POST", "attendance", data=payload)
        if response: st.success(response.get("message"))

def draw_educator_ui():
    st.header(f"Educator Dashboard: {st.session_state.username}")
    tabs = st.tabs(["Classroom", "Assignments", "Attendance", "AI Tutor Chat"])

    with tabs[0]: # Classroom Management
        classroom_details = api_request("GET", "classroom")
        if not classroom_details:
            st.error("Could not load classroom data.")
            return
        st.write(f"**Your Classroom Join Code:** `{classroom_details.get('join_code')}`")
        st.subheader("Pending Student Requests")
        pending_students = classroom_details.get("pending_student_ids", [])
        if not pending_students: st.write("No pending requests.")
        else:
            for student in pending_students:
                col1, col2 = st.columns([3, 1])
                col1.write(f"- {student}")
                if col2.button("Approve", key=f"approve_{student}"):
                    api_request("POST", f"classroom/approve/{student}")
                    st.success(f"Approved {student}!"); st.rerun()
        st.subheader("Current Students")
        current_students = classroom_details.get("student_ids", [])
        if not current_students: st.write("No students yet.")
        else: st.json(current_students)

    with tabs[1]: # Assignment Management
        st.subheader("Create New Assignment")
        with st.form("assignment_form"):
            title = st.text_input("Title")
            desc = st.text_area("Description")
            due_date = st.date_input("Due Date", min_value=datetime.date.today())
            submitted = st.form_submit_button("Create Assignment")
            if submitted and title:
                payload = {"title": title, "description": desc, "due_date": str(due_date)}
                api_request("POST", "assignments", data=payload); st.success("Assignment created!")
        st.subheader("Your Created Assignments")
        assignments = api_request("GET", "assignments/educator")
        if assignments:
            for a in assignments: st.write(f"**{a['title']}** (Due: {a['due_date']})")
        else: st.info("No assignments created yet.")

    with tabs[2]: # Attendance
        draw_attendance_ui()
    with tabs[3]: # AI Tutor Chat
        draw_chat_interface()

def draw_student_ui():
    st.header(f"👋 Student Dashboard: {st.session_state.username}")
    tab1, tab2, tab3 = st.tabs(["AI Tutor Chat", "Assignments", "Join Classroom"])

    with tab1: draw_chat_interface()
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
        else: st.info("You have no assignments yet.")
    with tab3:
        st.subheader("Join a Classroom")
        with st.form("join_classroom_form"):
            join_code = st.text_input("Enter Classroom Join Code")
            submitted = st.form_submit_button("Send Join Request")
            if submitted and join_code:
                response = api_request("POST", "classroom/join", data={"join_code": join_code})
                if response: st.success(response.get("message", "Request sent!"))

def draw_school_admin_ui():
    st.header(f"🏫 School Administration: {st.session_state.username}")
    st.subheader("Create a New School")
    with st.form("create_school_form"):
        school_name = st.text_input("School Name")
        submitted = st.form_submit_button("Create School")
        if submitted and school_name:
            response = api_request("POST", "schools", data={"name": school_name})
            if response:
                st.success(f"School '{school_name}' created successfully!")
                st.info(f"Your Educator Invite Code is: `{response.get('invite_code')}`")

def draw_login_screen():
    st.title("Welcome to the Educational AI Platform 🎓")
    with st.form("login_form"):
        username = st.text_input("Username")
        role = st.selectbox("Choose your role:", ["Student", "Educator", "School Admin"])
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
        st.header(f"👤 {st.session_state.username}")
        st.write(f"Role: **{st.session_state.role}**")
        if st.button("Logout"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
        st.divider()
        if st.session_state.role != "School Admin":
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
    elif st.session_state.role == "School Admin": draw_school_admin_ui()
    else: st.error("Invalid user role.")
