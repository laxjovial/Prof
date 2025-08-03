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
    # ... (full implementation)
    pass
def draw_storage_usage_ui():
    # ... (full implementation)
    pass
def draw_chat_interface():
    # ... (full implementation)
    pass
def draw_attendance_ui():
    # ... (full implementation)
    pass
def draw_educator_ui():
    # ... (full implementation)
    pass
def draw_student_ui():
    # ... (full implementation)
    pass

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
            st.session_state.username = username
            st.session_state.role = role
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
            # ... (AI config UI)
            st.divider()
            draw_rag_ui()
            st.divider()
            draw_storage_usage_ui()

    if st.session_state.role == "Student":
        draw_student_ui()
    elif st.session_state.role == "Educator":
        draw_educator_ui()
    elif st.session_state.role == "School Admin":
        draw_school_admin_ui()
    else:
        st.error("Invalid user role.")
