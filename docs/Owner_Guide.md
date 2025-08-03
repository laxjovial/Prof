# Owner's Guide: Educational AI Platform

## 1. Introduction

This document serves as the primary technical guide for the owner and maintainers of the Educational AI Platform. It provides a deep dive into the system's architecture, dependencies, configuration, and maintenance procedures.

## 2. System Architecture

The application is designed with a modern, decoupled client-server architecture to ensure scalability, maintainability, and flexibility.

-   **Backend (`main.py`)**: A FastAPI server that exposes the application's core logic through a RESTful API. It is responsible for all heavy lifting.
-   **Frontend (`app.py`)**: A Streamlit application that serves as a pure client. It handles all user interface elements and state management.
-   **Core Logic Modules**:
    -   `database.py`: Manages all interactions with Google Firestore.
    -   `ai.py`: An LLM abstraction layer for interacting with multiple AI providers.
    -   `rag.py`: Contains all functions for the RAG pipeline, including GCS interactions.
    -   `llm_config.py`: Configuration for supported LLM providers.
-   **Data Stores**:
    -   **Google Firestore**: A NoSQL database for all metadata (users, schools, classrooms, assignments, etc.).
    -   **Google Cloud Storage (GCS)**: An object store for the persistent storage of RAG vector stores.

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


The backend server requires a `.env` file with the following variables:

-   `TOGETHER_API_KEY`: API key for Together AI.
-   `OPENAI_API_KEY`: API key for OpenAI.
-   `GOOGLE_API_KEY`: API key for Google's generative AI services.
-   `API_BASE_URL`: The URL for the FastAPI backend itself (used by the frontend). Defaults to `http://127.0.0.1:8000`.
-   `GCS_BUCKET_NAME`: The name of the GCS bucket to use for RAG storage.
-   `USER_STORAGE_LIMIT_MB`: The universal storage quota for each user in megabytes.
-   `GOOGLE_APPLICATION_CREDENTIALS`: The path to the JSON service account key file for authenticating with all Google Cloud services (Firestore and GCS).

### Streamlit Secrets

The frontend (`app.py`) uses Streamlit's secrets (`.streamlit/secrets.toml`) to initialize its own independent connection to Firestore for some client-side operations. This should contain the `firestore_key`.

-   `TOGETHER_API_KEY`: Your API key for the Together AI service.
-   `API_BASE_URL`: The URL for the FastAPI backend (e.g., `http://127.0.0.1:8000`).
-   `GCS_BUCKET_NAME`: The name of the Google Cloud Storage bucket used for persistent RAG vector store storage.

### Secrets Management

Sensitive keys are managed in `.streamlit/secrets.toml` for the frontend. For production deployment of the backend, these should be injected securely as environment variables.


## 4. Maintenance & Deployment

### Running Locally

You must run the backend and frontend servers in two separate terminals.


1.  **Start Backend**:
    ```bash
    uvicorn main:app --reload
    ```
2.  **Start Frontend**:
    ```bash
    streamlit run app.py
    ```

### Production Deployment

1.  **Containerize**: Create separate `Dockerfile`s for the FastAPI backend and the Streamlit frontend.
2.  **Backend Server**: Use a production-grade ASGI server like Gunicorn with Uvicorn workers to run the FastAPI app.
3.  **Secrets**: In production, do not use `.env` files. Inject all environment variables and the Google service account key securely using the deployment platform's secrets management system (e.g., Kubernetes Secrets, Docker Swarm Secrets, Google Secret Manager).
4.  **Orchestration**: Deploy the containers using a service like Docker Compose, Kubernetes, or a cloud provider's container service (e.g., Google Cloud Run, AWS Fargate).

### Backups

-   **Firestore**: Regularly schedule backups of your Firestore database using the GCP console or `gcloud` commands.
-   **GCS**: Enable versioning on your GCS bucket to protect against accidental deletion of user RAG files.

## 5. Troubleshooting

-   **401 Unauthorized**: The `X-Username` header is missing from an API request. This is handled automatically by the frontend but could be an issue if using the API directly.
-   **403 Forbidden**: The user associated with the `X-Username` header does not have the required role (e.g., "Educator") for the endpoint.
-   **413 Payload Too Large**: A user has tried to upload a file that exceeds their storage quota.
-   **500 Internal Server Error**: Check the backend server logs for tracebacks. Common causes include missing environment variables on startup or errors from external APIs (LLMs, Google Cloud).

1.  **Start Backend**: `uvicorn main:app --reload`
2.  **Start Frontend**: `streamlit run app.py`

### Deployment

A production deployment would involve containerizing the frontend and backend (e.g., with Docker) and deploying them to a cloud service. A production-grade process manager like Gunicorn should be used for the FastAPI server.

