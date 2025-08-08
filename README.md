
# Educational AI Platform & Learning Management System (LMS) - Production Version

This project is a sophisticated, multi-component Educational AI Platform architected to function as a full-fledged, multi-tenant Learning Management System (LMS) for individuals, educators, and institutions. It is built with a production-ready, secure, and scalable architecture.

## 🏛️ Architecture

-   **Backend**: A secure API built with **FastAPI**, featuring JWT token-based authentication.
-   **Frontend**: An interactive web application built with **Streamlit**, acting as a pure client to the backend.
-   **Core Logic**: A modular library of functions separated by concern (`database.py`, `ai.py`, `rag.py`, `auth.py`, `llm_config.py`).
-   **Data Stores**: **Google Firestore** for all application metadata and **Google Cloud Storage** for persistent, secure storage of user-uploaded documents and AI vector stores.

## ✨ Key Features

-   **Secure Authentication**: Production-grade login/registration system using password hashing and JWT access tokens.
-   **Multi-Tenant Hierarchy**: Full support for `School -> Educator -> Student` relationships, as well as independent educators and individual learners.
-   **Secure Classroom Management**: A complete workflow for educators to manage their classroom with unique join codes and an approval system.
-   **Multi-LLM Support**: A flexible backend that can use multiple AI providers (Together AI, OpenAI, Google, etc.), selectable by the user in the UI.
-   **Persistent & Categorized RAG**: A powerful RAG system where users can upload multiple documents, assign them to categories, and have them permanently stored and secured in Google Cloud Storage.
-   **Configurable Storage Quotas**: A universal, per-user storage limit, configurable by the platform owner, prevents misuse.
-   **Full Assessment & Grading Cycle**: Educators can create assignments with deadlines, and students can submit their work to be graded instantly by the AI.
-   **Comprehensive Documentation**: Includes in-app user guides and a full suite of project documents in the `/docs` directory.

## 🚀 Production Setup and Installation

### 1. Set Up Credentials & Environment

Create a `.env` file and populate it with your secret keys and configuration:
```
# .env

# --- LLM API Keys ---

TOGETHER_API_KEY="your_key_here"
OPENAI_API_KEY="your_key_here"
GOOGLE_API_KEY="your_key_here"


# --- JWT Secret ---
# Generate a strong, random string for this in production, e.g., openssl rand -hex 32
JWT_SECRET_KEY="your_super_secret_jwt_key"

# --- Backend & Storage Config ---
API_BASE_URL="http://127.0.0.1:8000"
GCS_BUCKET_NAME="your-gcs-bucket-name-for-rag-storage"
USER_STORAGE_LIMIT_MB="100"

# --- Google Cloud Service Account ---

# Provide the absolute path to your service account key file
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```


### 3. Run the Application
You must run the backend and frontend servers in **two separate terminals**.

**Terminal 1: Start Backend Server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2: Start Frontend Application**
```bash
streamlit run app.py
```
Your application will be accessible at the local URL provided by Streamlit.
