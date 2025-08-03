import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

@st.cache_resource
def create_vector_store(_docs, embeddings):
    """Creates a FAISS vector store from documents."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(_docs)
    return FAISS.from_documents(texts, embeddings)
