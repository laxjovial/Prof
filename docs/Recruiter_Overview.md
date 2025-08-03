# Recruiter's Overview: Educational AI Platform Project

## 1. Project Synopsis

This project is a full-stack, AI-powered educational platform demonstrating a wide range of modern software engineering skills. It was built from a simple script into a robust, scalable, and feature-rich application with a decoupled frontend and backend. The platform serves as an adaptive, persona-driven tutor that can be grounded in user-provided documents, with all data being persistent in the cloud.

## 2. Technical Architecture & Skills Demonstrated

This project showcases expertise in the following areas:

### a. Full-Stack Development & API Design

-   **Backend**: A RESTful API was designed and built from the ground up using **FastAPI**. This demonstrates proficiency in modern Python web frameworks, API design principles, Pydantic data modeling, and dependency injection.
-   **Frontend**: A clean, responsive user interface was built with **Streamlit**. The frontend was refactored from a monolithic script into a pure client that communicates with the backend, demonstrating an understanding of client-server architecture.
-   **Client-Server Communication**: The frontend uses the `requests` library to interact with the backend, showcasing knowledge of HTTP methods and data serialization (JSON).

### b. Cloud & DevOps

-   **Cloud Services**: The project leverages multiple **Google Cloud Platform (GCP)** services, demonstrating experience with cloud-native development:
    -   **Google Firestore**: For persistent, scalable NoSQL database storage of user chat histories.
    -   **Google Cloud Storage (GCS)**: For secure, persistent object storage of processed RAG vector stores.
-   **Architecture**: The decoupled client-server model is a modern, scalable architecture suitable for containerization (e.g., Docker) and cloud deployment.
-   **Environment & Secret Management**: The project correctly uses `.env` files for local configuration and `streamlit.secrets` for managing sensitive API keys, showcasing an understanding of security best practices.

### c. AI & Machine Learning Engineering

-   **Large Language Models (LLMs)**: The application integrates with the **Together AI** API, demonstrating the ability to work with and control modern generative AI models.
-   **Retrieval-Augmented Generation (RAG)**: A complete, persistent RAG pipeline was implemented using **LangChain**. This includes:
    -   **Document Loading & Processing**: Handling `.pdf` and `.txt` files.
    -   **Embeddings**: Using embedding models to convert text to vectors.
    -   **Vector Store**: Using **FAISS** for efficient similarity search.
    -   **Persistence**: Saving and loading the FAISS index to/from Google Cloud Storage.

### d. Software Engineering Best Practices

-   **Modular Design**: The codebase was refactored from a single script into a highly modular structure with logic separated by concern (`database.py`, `ai.py`, `rag.py`). This demonstrates a commitment to writing clean, maintainable, and scalable code.
-   **User-Centric Design**: Iteratively added features based on user feedback (e.g., the RAG toggle, multipage UI, and major architectural changes).

This project serves as a strong portfolio piece, demonstrating the ability to design, build, and deploy a complex, full-stack, cloud-native AI application from the ground up.
