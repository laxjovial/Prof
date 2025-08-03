
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

# Educational AI Platform

This project is a sophisticated, multi-component Educational AI Platform featuring a distinct frontend, backend, and a modular logic core. It's designed to act as a versatile learning and teaching assistant, capable of adopting any expert persona, generating a wide range of educational content, and grounding its knowledge in user-provided documents.

## 🏛️ Architecture

The application is built with a modern client-server architecture:

- **Backend**: A robust API built with **FastAPI**, serving all the core business logic.
- **Frontend**: An interactive web application built with **Streamlit**, acting as a pure client to the backend.
- **Core Logic**: A modular library of functions separated by concern (`database.py`, `ai.py`, `rag.py`).

## ✨ Key Features

- **Dynamic AI Persona & Level**: Configure the AI's persona and educational complexity via the UI.
- **Persistent User Sessions**: Chat history is saved to Firestore, allowing users to resume sessions.
- **Persistent Document Context (RAG)**: Upload documents (`.pdf`, `.txt`) for the AI to use as a primary, context-aware knowledge source. The processed documents are saved to Google Cloud Storage, ensuring they are persistent across sessions.
- **Granular Control**: Toggle the use of document context (RAG) on or off for any query.
- **Rich Content Generation**: Create curricula, syllabi, and tests on the fly.
- **Multipage UI**: A clean, multi-page interface separating the main chat application from the user guide.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Core AI/RAG**: LangChain, Together AI
- **Database**: Google Firestore
- **Deployment**: Client-Server Model

## 🚀 Setup and Installation

Follow these steps to run the entire application suite locally.

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

Create a `.env` file for environment variables:
```
# .env
TOGETHER_API_KEY="your_together_ai_key_here"
API_BASE_URL="http://127.0.0.1:8000"
GCS_BUCKET_NAME="your-gcs-bucket-name-for-rag-storage"
```

Create a `.streamlit/secrets.toml` file for Streamlit secrets (for the frontend to connect to the database):

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


You need to run the backend and frontend servers in **two separate terminals**.

**Terminal 1: Start the Backend Server**
```bash
uvicorn main:app --reload
```
The backend API will be available at `http://127.0.0.1:8000`.

**Terminal 2: Start the Frontend Application**
```bash
streamlit run app.py
```
Open your browser to the local URL provided by Streamlit to use the application.

## 📖 How to Use

1.  **Login**: Enter a username in the sidebar on the main "Chat" page.
2.  **Navigate**: Use the sidebar to switch between the "Chat" page and the "User Guide".
3.  **Configure & Chat**: Set the AI's persona and educational level, then start your conversation.
4.  **Upload Documents**: Use the file uploader to provide context documents to the AI. Click "Process Document" to send it to the backend.

