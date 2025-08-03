# Educational AI Platform

This project transforms a basic LLM interaction tool into a comprehensive, persona-driven Educational AI Platform. It's designed to act as a versatile learning and teaching assistant, capable of adopting any expert persona, generating a wide range of educational content, and grounding its knowledge in user-provided documents.

## ✨ Key Features

- **Dynamic AI Persona**: Define any expert persona for the AI (e.g., "Quantum Physics Professor," "First Grade Reading Teacher," "Financial Analyst").
- **Customizable Educational Level**: Tailor the AI's teaching style and content complexity to a specific educational level (e.g., "University," "Middle School," "Beginner").
- **Persistent User Sessions**: A simple username system allows users to log in and have their conversation history saved. Your session resumes right where you left off.
- **Rich Content Generation**: Generate a variety of educational materials based on your conversation, including:
  - Full Curriculums
  - Detailed Syllabi
  - Tests and Quizzes
- **Retrieval-Augmented Generation (RAG)**:
  - **Upload Your Materials**: Upload your own documents (`.pdf`, `.txt`). The AI will use these as a primary source of information.
  - **Context-Aware Q&A**: The AI's answers will be grounded in the content of your uploaded documents.
  - **Generate Questions from Documents**: Create relevant test questions based on your uploaded materials.
- **Toggle RAG Context**: A checkbox allows you to temporarily disable the document context for specific queries, giving you full control over the AI's knowledge base.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM & Embeddings**: Together AI
- **Database**: Google Firestore (for persistent chat history)
- **RAG Pipeline**: LangChain, FAISS Vector Store

## 🚀 Setup and Installation

Follow these steps to run the application locally.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Set Up Credentials

This application requires API keys for both Together AI and Google Firestore. These are managed using Streamlit's secrets management.

Create a file at `.streamlit/secrets.toml` and add the following content:

```toml
# .streamlit/secrets.toml

# Your Together AI API Key
TOGETHER_API_KEY = "your_api_key_here"

# Your Google Cloud Firestore Service Account Key
# The entire JSON key file content must be enclosed in a single string.
# Make sure to escape any special characters within the JSON string if necessary.
firestore_key = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-client-email@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-client-email.iam.gserviceaccount.com"
}
'''
```

### 3. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Launch the Streamlit application.

```bash
streamlit run app.py
```

The application should now be open and running in your web browser.

## 📖 How to Use

1.  **Login**: Enter a username in the sidebar to start a new session or resume a previous one.
2.  **Configure the AI**:
    -   Set the **AI Persona** to define its role.
    -   Optionally, set the **Educational Level** to adjust content complexity.
3.  **Chat**: Start your conversation in the main chat window. Your history is saved automatically.
4.  **Upload a Document**:
    -   Use the file uploader in the sidebar to select a `.pdf` or `.txt` file.
    -   Click **"Process Document"**. The AI will now use this document for context.
    -   To temporarily ignore the document, uncheck the **"Use Document Context"** box.
5.  **Generate Content**: Use the buttons in the sidebar to generate curricula, syllabi, or tests based on your conversation.
