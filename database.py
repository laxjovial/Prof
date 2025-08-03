import streamlit as st
from google.cloud import firestore
import json

@st.cache_resource
def init_firestore():
    """
    Initializes a connection to Google Firestore using credentials from Streamlit secrets.
    """
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

def load_chat_history(db: firestore.Client, username: str):
    """
    Loads chat history for a given user from Firestore.
    """
    doc_ref = db.collection("chat_histories").document(username)
    doc = doc_ref.get()
    return doc.to_dict().get("messages", []) if doc.exists else []

def save_chat_history(db: firestore.Client, username: str, messages: list):
    """
    Saves chat history for a given user to Firestore.
    """
    doc_ref = db.collection("chat_histories").document(username)
    doc_ref.set({"messages": messages})
