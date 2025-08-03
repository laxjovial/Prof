import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json

# Local Imports
# The frontend still handles DB history and initialization
import database

# Load environment variables from .env file
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Educational AI Platform",
    page_icon="🎓",
    layout="wide"
)

# --- API Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# --- Helper Functions for API calls ---
def post_to_backend(endpoint: str, data: dict = None, files: dict = None):
    """Helper function to post data or files to the backend."""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if files:
            response = requests.post(url, files=files)
        else:
            response = requests.post(url, json=data)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend: {e}")
        return None

# --- Main App ---
st.title("🎓 Educational AI Platform")

# --- Firestore Initialization ---
# The frontend will continue to manage chat history persistence.
db = database.init_firestore()

# --- Sidebar ---
with st.sidebar:
    st.header("👤 User")
    if 'username' in st.session_state:
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        username_input = st.text_input("Enter a username to begin:", key="username_input")
        if st.button("Login"):
            if username_input:
                st.session_state.username = username_input
                st.rerun()
            else:
                st.warning("Please enter a username.")

    st.markdown("---")

    if 'username' in st.session_state:
        st.header("⚙️ Configuration")
        st.subheader("🤖 AI Persona")
        st.session_state.ai_persona = st.text_input("Define AI's expert persona:", st.session_state.get("ai_persona", "You are a helpful assistant."))
        st.subheader("📚 Educational Level")
        st.session_state.educational_level = st.text_input("Specify educational level (optional):", st.session_state.get("educational_level", ""))

        st.subheader("📎 Upload & Process Document")
        uploaded_file = st.file_uploader("Upload PDF, TXT", type=['pdf', 'txt'])
        if uploaded_file:
            if st.button("Process Document"):
                with st.spinner("Sending document to backend for processing..."):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    endpoint = f"upload-document/{st.session_state.username}"
                    response = post_to_backend(endpoint, files=files)
                    if response:
                        st.session_state.doc_id = response.get("doc_id")
                        st.success(response.get("message"))
                    else:
                        st.error("Failed to process document.")

        use_rag_toggle = True
        if 'doc_id' in st.session_state:
            use_rag_toggle = st.checkbox("Use Document Context", value=True, key="use_rag")
            if st.button("Generate Questions from Document"):
                q_prompt = "Based on the provided document context, generate a set of 5-7 diverse questions..."
                st.session_state.messages.append({"role": "user", "content": q_prompt})
                st.rerun()

# --- Chat Interface ---
if 'username' in st.session_state:
    username = st.session_state.username

    if "messages" not in st.session_state:
        st.session_state.messages = database.load_chat_history(db, username)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to learn about?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                payload = {
                    "username": username,
                    "messages": st.session_state.messages,
                    "persona": st.session_state.ai_persona,
                    "educational_level": st.session_state.educational_level,
                    "use_rag": use_rag_toggle,
                    "doc_id": st.session_state.get("doc_id")
                }
                response_data = post_to_backend("chat", data=payload)

                if response_data:
                    ai_response = response_data.get("content")
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    database.save_chat_history(db, username, st.session_state.messages)
                else:
                    st.session_state.messages.pop() # Remove user prompt if API fails
                    st.error("Failed to get response from the backend.")
else:
    st.info("Please enter a username in the sidebar to start your session.")
