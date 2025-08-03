import streamlit as st
from together import Together
from dotenv import load_dotenv
import os
from google.cloud import firestore
import json
import tempfile

# --- Langchain Imports ---
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_together import TogetherEmbeddings

# Load environment variables from .env file
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Educational AI Platform",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Educational AI Platform")

# --- Firestore Connection ---
@st.cache_resource
def init_firestore():
    try:
        if "firestore_key" in st.secrets:
            key_dict = json.loads(st.secrets["firestore_key"])
            db = firestore.Client.from_service_account_info(key_dict)
            return db
        else:
            st.error("Firestore credentials not found in Streamlit secrets.")
            st.stop()
    except Exception as e:
        st.error(f"Failed to connect to Firestore: {e}")
        st.stop()

# --- Database Functions ---
def load_chat_history(db: firestore.Client, username: str):
    doc_ref = db.collection("chat_histories").document(username)
    doc = doc_ref.get()
    return doc.to_dict().get("messages", []) if doc.exists else []

def save_chat_history(db: firestore.Client, username: str, messages: list):
    doc_ref = db.collection("chat_histories").document(username)
    doc_ref.set({"messages": messages})

# --- RAG and AI Functions ---
@st.cache_resource
def create_vector_store(_docs, embeddings):
    """Creates a FAISS vector store from documents."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(_docs)
    return FAISS.from_documents(texts, embeddings)

def get_ai_response(client, system_prompt, messages, vector_store=None):
    """Generates a response from the Together AI API, augmented with RAG context if available."""
    prompt = messages[-1]['content']
    context = ""
    if vector_store:
        docs = vector_store.similarity_search(prompt, k=3)
        context = "\n\n---\n\nContext from uploaded document:\n" + "\n".join([d.page_content for d in docs])

    final_prompt = prompt + context

    try:
        api_messages = [{"role": "system", "content": system_prompt}] + messages[:-1] + [{"role": "user", "content": final_prompt}]
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=api_messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred with the AI API: {e}")
        return None

# --- Main App Logic ---
db = init_firestore()

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
        secret_key = os.getenv("api_key") or st.secrets.get("TOGETHER_API_KEY")
        if not secret_key:
            st.warning("Together AI Key not found.")
            secret_key = st.text_input("Enter your Together AI API Key", type="password", key="api_key_input")

        if secret_key:
            client = Together(api_key=secret_key)
            embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval", api_key=secret_key)
        else:
            st.error("An API Key is required.")
            st.stop()

        st.subheader("🤖 AI Persona")
        ai_persona = st.text_input("Define AI's expert persona:", "You are a helpful and knowledgeable assistant.", key="persona")
        st.subheader("📚 Educational Level")
        educational_level = st.text_input("Specify educational level (optional):", key="level")

        system_prompt = f"{ai_persona} You are teaching at a {educational_level} level." if educational_level else ai_persona

        st.subheader("📝 Generate Content")
        content_buttons = {"Curriculum": "Generate a comprehensive curriculum.", "Syllabus": "Generate a syllabus.", "Test": "Create a test."}
        for label, prompt in content_buttons.items():
            if st.button(f"Generate {label}"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                # RAG context will be added automatically by get_ai_response
                st.rerun()

        st.subheader("📎 Upload & Process Document")
        uploaded_file = st.file_uploader("Upload PDF, TXT", type=['pdf', 'txt'])
        if uploaded_file:
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    if uploaded_file.type == "application/pdf":
                        loader = PyPDFLoader(tmp_file_path)
                    else:
                        loader = TextLoader(tmp_file_path)

                    docs = loader.load()
                    st.session_state.vector_store = create_vector_store(docs, embeddings)
                    os.remove(tmp_file_path)
                    st.success("Document processed and ready for Q&A!")

        if 'vector_store' in st.session_state:
            st.success("Document loaded. AI will now use it for context.")
            if st.button("Generate Questions from Document"):
                q_prompt = "Based on the provided document context, generate a set of 5-7 diverse questions (e.g., multiple choice, short answer, conceptual) that would be suitable for a test."
                st.session_state.messages.append({"role": "user", "content": q_prompt})
                st.rerun()

# --- Chat Interface ---
if 'username' in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history(db, st.session_state.username)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to learn about?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Trigger AI response if the last message is from the user
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                vector_store = st.session_state.get('vector_store')
                ai_response = get_ai_response(client, system_prompt, st.session_state.messages, vector_store)
                if ai_response:
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    save_chat_history(db, st.session_state.username, st.session_state.messages)
                else:
                    st.session_state.messages.pop() # Remove user prompt if AI fails
else:
    st.info("Please enter a username in the sidebar to start your session.")
    st.warning("Please ensure you have set up your Firestore and Together AI credentials in your Streamlit secrets.", icon="🔑")
    st.code("""
    # In your .streamlit/secrets.toml file:

    firestore_key = "{\\"type\\": \\"service_account\\", ...}"
    TOGETHER_API_KEY = "your_api_key_here"
    """)
