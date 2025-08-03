# Educational AI Platform & Learning Management System (LMS)

This project is a sophisticated, multi-component Educational AI Platform featuring a distinct frontend, backend, and a modular logic core. It has been architected to function as a full-fledged, multi-tenant Learning Management System (LMS) for individuals, educators, and institutions.

## 🏛️ Architecture

The application is built with a modern, scalable client-server architecture:

-   **Backend**: A robust API built with **FastAPI**.
-   **Frontend**: An interactive web application built with **Streamlit**.
-   **Core Logic**: A modular library of functions separated by concern (`database.py`, `ai.py`, `rag.py`, `llm_config.py`).
-   **Data Stores**: **Google Firestore** for metadata and **Google Cloud Storage** for persistent document/vector storage.

## ✨ Key Features

-   **Multi-Tenant System**: Full support for a `School -> Educator -> Student` hierarchy, as well as independent educators and individual learners.
-   **Secure Classroom Management**: A complete workflow for educators to manage their classroom with unique join codes and an approval system for new students.
-   **Multi-LLM Support**: The platform is LLM-agnostic. Users can choose their preferred AI provider (e.g., Together AI, OpenAI, Google) from the UI.
-   **Persistent & Categorized RAG**:
    -   Upload multiple documents (`.pdf`, `.txt`) and assign them to user-defined categories.
    -   Vector stores are persisted securely in Google Cloud Storage.
    -   A universal, configurable storage limit per user prevents misuse.
-   **Full Assessment Cycle**:
    -   Educators can create assignments with deadlines.
    -   Students can submit their work.
    -   An AI-powered engine grades submissions and provides instant, constructive feedback.
-   **Attendance Tracking**: A simple UI for educators to mark daily student attendance.
-   **Comprehensive Documentation**: Includes in-app user guides for different roles and a full suite of project documents in the `/docs` directory.

## 🚀 Setup and Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Set Up Credentials & Environment

Create a `.env` file and populate it with your API keys and configuration:
```
# .env
# --- LLM API Keys (add all you want to use) ---
TOGETHER_API_KEY="your_key_here"
OPENAI_API_KEY="your_key_here"
GOOGLE_API_KEY="your_key_here"

# --- Backend & Storage Config ---
API_BASE_URL="http://127.0.0.1:8000"
GCS_BUCKET_NAME="your-gcs-bucket-name-for-rag-storage"
USER_STORAGE_LIMIT_MB="100"

# --- Google Cloud Service Account ---
# The backend uses this env var to find the key file
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

Create a `.streamlit/secrets.toml` file for the frontend's database connection:
```toml
# .streamlit/secrets.toml
firestore_key = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
'''
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
You must run the backend and frontend servers in **two separate terminals**.

**Terminal 1: Start Backend**
```bash
uvicorn main:app --reload
```

**Terminal 2: Start Frontend**
```bash
streamlit run app.py
```
