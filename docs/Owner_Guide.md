# Owner's Guide: Educational AI Platform

## 1. Introduction

This document serves as the primary technical guide for the owner and maintainers of the Educational AI Platform. It provides a deep dive into the system's architecture, dependencies, configuration, and maintenance procedures.

## 2. System Architecture

The application is designed with a modern, decoupled client-server architecture to ensure scalability, maintainability, and flexibility.

-   **Backend (`main.py`)**: A FastAPI server that exposes the application's core logic through a RESTful API.
-   **Frontend (`app.py`)**: A Streamlit application that serves as a pure client.
-   **Core Logic Modules**:
    -   `database.py`: Manages the connection to Google Firestore.
    -   `ai.py`: Contains the logic for interacting with the Together AI API.
    -   `rag.py`: Contains all functions related to the RAG pipeline.

### 2.1. RAG Storage Mechanism

The vector stores generated from user-uploaded documents are persisted to **Google Cloud Storage (GCS)**.

-   When a user uploads a document, the backend processes it into a FAISS vector store.
-   This vector store is then saved as a set of files to a dedicated GCS bucket.
-   When a user makes a request, the backend retrieves the relevant vector store from GCS, loads it into memory, and uses it for the RAG process.
-   This ensures that a user's document context is persistent across sessions and server restarts.

## 3. Configuration

### Environment Variables

-   `TOGETHER_API_KEY`: Your API key for the Together AI service.
-   `API_BASE_URL`: The URL for the FastAPI backend (e.g., `http://127.0.0.1:8000`).
-   `GCS_BUCKET_NAME`: The name of the Google Cloud Storage bucket used for persistent RAG vector store storage.

### Secrets Management

Sensitive keys are managed in `.streamlit/secrets.toml` for the frontend. For production deployment of the backend, these should be injected securely as environment variables.

## 4. Maintenance & Deployment

### Running Locally

You must run the backend and frontend servers in two separate terminals.

1.  **Start Backend**: `uvicorn main:app --reload`
2.  **Start Frontend**: `streamlit run app.py`

### Deployment

A production deployment would involve containerizing the frontend and backend (e.g., with Docker) and deploying them to a cloud service. A production-grade process manager like Gunicorn should be used for the FastAPI server.
