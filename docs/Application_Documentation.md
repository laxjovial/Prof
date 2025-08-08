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

│   ├── ... (other guides)
├── pages/
│   ├── ... (guide pages)
├── ai.py
├── app.py
├── database.py
├── llm_config.py

├── main.py
├── rag.py
└── requirements.txt
```

## 3. Core Logic Modules

These modules contain the business logic and are designed to be independent of the web frameworks.

### `database.py`

-   **Purpose**: Handles all interactions with the Google Firestore database.

-   **Key Functions**: `init_firestore`, `get_or_create_user`, `create_school`, `join_school`, `get_classroom_details`, `request_to_join_classroom`, `approve_student_join_request`, `add_document_metadata`, `create_assignment`, `save_submission`, `mark_attendance`.

### `rag.py`

-   **Purpose**: Contains all functions related to the RAG pipeline.


-   **Key Functions**: `init_firestore`, `get_or_create_user`, `create_school`, `join_school`, `get_classroom_details`, `request_to_join_classroom`, `approve_student_join_request`, `add_document_metadata`, `create_assignment`, `save_submission`, `mark_attendance`.

-   **Functions**:
    -   `init_firestore()`: Initializes and returns a Firestore client instance.
    -   `load_chat_history(db, username)`: Fetches chat history from Firestore.
    -   `save_chat_history(db, username, messages)`: Saves chat history to Firestore.


### `rag.py`

-   **Purpose**: Contains all functions related to the RAG pipeline.

-   **Key Functions**: `create_vector_store`, `save_vector_store_to_gcs`, `load_vector_store_from_gcs`, `get_user_storage_usage_mb`.

### `ai.py`

-   **Purpose**: Manages all direct interactions with the LLMs. This is the LLM abstraction layer.
-   **Key Functions**: `get_ai_response`. This function takes a `provider` string (e.g., "OpenAI") and dynamically calls the correct client and formats the request accordingly.

### `llm_config.py`

-   **Purpose**: A configuration file that holds the settings for the various supported LLM providers, such as model names and required environment variable keys.


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

-   **Startup Event**: Initializes the database connection, embeddings model, and loads environment variables like the GCS bucket name and storage limit.
-   **Dependencies**: Uses FastAPI's `Depends` system to simulate user authentication (`get_current_user`) and role-based authorization (`get_current_educator`).
-   **Endpoints**: Exposes the core logic via endpoints like `/chat`, `/documents` (for upload), `/classroom/*`, `/assignments`, and `/submissions/grade`.


## 5. Frontend (Streamlit)

### `app.py`


-   **Purpose**: The main entry point for the user-facing application. Acts as a pure client to the backend.
-   **API Communication**: Contains a helper function `api_request` to handle all HTTP requests to the FastAPI server.
-   **UI Dispatcher**: The main logic of the app checks if a user is logged in. If not, it shows `draw_login_screen`. If they are, it uses the user's `role` from `st.session_state` to call the appropriate UI drawing function (`draw_student_ui` or `draw_educator_ui`).
-   **UI Components**: Each major piece of UI is encapsulated in its own `draw_*` function for clarity and modularity.

### `pages/`

-   **Purpose**: Implements the multipage functionality of the Streamlit app.
-   **Content**: Each file in this directory corresponds to a page in the navigation sidebar (e.g., `1_General_User_Guide.py`). These pages read the corresponding `.md` files from the `docs/` directory and display them.
