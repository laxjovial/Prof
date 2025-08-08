from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google.cloud import storage
import tempfile
import os
from pathlib import Path

def create_vector_store(docs, embeddings):
    """Creates a FAISS vector store from documents."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)
    vector_store = FAISS.from_documents(texts, embeddings)
    return vector_store

def save_vector_store_to_gcs(vector_store, bucket_name, destination_blob_prefix):
    """Saves a FAISS vector store to a GCS bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the FAISS index to a temporary local directory
            vector_store.save_local(temp_dir)

            # Upload each file in the temp directory to GCS
            for file_path in Path(temp_dir).rglob('*'):
                if file_path.is_file():
                    blob_name = f"{destination_blob_prefix}/{file_path.name}"
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(str(file_path))

        print(f"Vector store saved to GCS bucket '{bucket_name}' with prefix '{destination_blob_prefix}'")
        return True
    except Exception as e:
        print(f"Failed to save vector store to GCS: {e}")
        return False

def load_vector_store_from_gcs(bucket_name, source_blob_prefix, embeddings):
    """Loads a FAISS vector store from a GCS bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Download all parts of the FAISS index from GCS

            blobs = list(storage_client.list_blobs(bucket_name, prefix=source_blob_prefix))
            if not blobs:
                return None # No document found for this user/scope


            for blob in blobs:
                file_name = os.path.basename(blob.name)
                destination_file_path = os.path.join(temp_dir, file_name)
                blob.download_to_filename(destination_file_path)


            # Load the FAISS index from the temporary directory
            vector_store = FAISS.load_local(temp_dir, embeddings, allow_dangerous_deserialization=True)
            print(f"Vector store loaded from GCS bucket '{bucket_name}'")
            return vector_store

    except Exception as e:
        print(f"Failed to load vector store from GCS: {e}")
        return None


def get_user_storage_usage_mb(bucket_name: str, username: str) -> float:
    """Calculates the total storage size in MB for a given user's folder in GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    prefix = f"vector_stores/{username}/"
    blobs = storage_client.list_blobs(bucket, prefix=prefix)

    total_size_bytes = sum(blob.size for blob in blobs)
    total_size_mb = total_size_bytes / (1024 * 1024)
    return total_size_mb

