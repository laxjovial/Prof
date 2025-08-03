# Application Technical Documentation

## 1. Overview

This document provides a detailed technical breakdown of the files and code structure of the Educational AI Platform. It is intended for developers who will be working on or maintaining the codebase.

## 2. File Structure

```
.
├── .env
├── .streamlit/
│   └── secrets.toml
├── docs/
│   ├── Application_Documentation.md
│   ├── Investor_Briefing.md
│   ├── Owner_Guide.md
│   ├── Recruiter_Overview.md
│   └── User_Guide.md
├── pages/
│   └── 1_User_Guide.py
├── ai.py
├── app.py
├── database.py
├── main.py
├── rag.py
└── requirements.txt
```

## 3. Core Logic Modules

These modules contain the business logic and are designed to be independent of the web frameworks.

### `database.py`

-   **Purpose**: Handles all interactions with the Google Firestore database.
-   **Functions**:
    -   `init_firestore()`: Initializes and returns a Firestore client instance.
    -   `load_chat_history(db, username)`: Fetches chat history from Firestore.
    -   `save_chat_history(db, username, messages)`: Saves chat history to Firestore.

### `rag.py`

-   **Purpose**: Contains all functions related to the RAG pipeline.
-   **Functions**:
    -   `create_vector_store(docs, embeddings)`: Creates a FAISS vector store from processed documents.
    -   `save_vector_store_to_gcs(...)`: Saves a FAISS index to a GCS bucket.
    -   `load_vector_store_from_gcs(...)`: Loads a FAISS index from a GCS bucket.

### `ai.py`

-   **Purpose**: Manages all direct interactions with the Together AI LLM.
-   **Functions**:
    -   `get_ai_response(...)`: The core AI function. It augments a prompt with RAG context (if applicable) and calls the Together AI API.

## 4. Backend (FastAPI)

### `main.py`

-   **Purpose**: Defines and serves the backend RESTful API.
-   **Startup Event**: Initializes the Together AI client, embeddings model, and gets the GCS bucket name from environment variables.
-   **Endpoints**:
    -   `POST /upload-document/{username}`: Receives a file, processes it into a vector store using `rag.py`, and saves the persistent index to Google Cloud Storage.
    -   `POST /chat`: Receives chat context from the frontend. It loads the corresponding vector store from GCS (if RAG is toggled on), passes the request to `ai.py` to get the AI response, and returns the response to the frontend.

## 5. Frontend (Streamlit)

### `app.py`

-   **Purpose**: The main entry point for the user-facing application and the primary chat interface.
-   **API Communication**: Contains a helper function `post_to_backend` to handle all communication with the FastAPI server.
-   **Workflow**:
    1.  UI elements collect user input into `st.session_state`.
    2.  User actions trigger calls to the FastAPI backend.
    3.  The frontend receives the backend's response and updates the UI.
    4.  The frontend directly communicates with Firestore to save and load chat history, keeping the backend stateless in that regard.

### `pages/1_User_Guide.py`

-   **Purpose**: A secondary page in the Streamlit multipage app.
-   **Functionality**: Reads `docs/User_Guide.md` and displays it.
