import os
import json
from .constants import PDF_DIR, SPLITS_CACHE_PATH, EMBEDDING_MODEL_PATH, DOCUMENTS_SPLITTED_PATH
import torch
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import pickle

device = "cuda" if torch.cuda.is_available() else "cpu"

def load_docs(folder=PDF_DIR):
    """Return all PDF file paths in a folder recursively."""
    document_loader = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.abspath(os.path.join(root, file))
            document_loader.append(full_path)
    return document_loader


def split_single_document(document):
    """Split a single document into text chunks."""
    loader = PyMuPDFLoader(document)
    doc = loader.load()

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512,
        chunk_overlap=64,
    )
    return text_splitter.split_documents(doc)


def embeddings(embedding_model):
    """Return HuggingFace embeddings object for the given model."""
    return HuggingFaceEmbeddings(
        model=embedding_model,
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True}
    )


def create_splits(documents):
    """Split all new documents into chunks and return the full list of splits."""
    # Load previously processed file list
    if os.path.exists(DOCUMENTS_SPLITTED_PATH):
        with open(DOCUMENTS_SPLITTED_PATH, "r", encoding="utf-8") as f:
            processed_files = set(json.load(f).get("files", []))
    else:
        processed_files = set()

    # Identify new documents
    new_docs = [doc for doc in documents if doc not in processed_files]

    # Load cached splits
    if os.path.exists(SPLITS_CACHE_PATH):
        print("Loading cached splits from disk")
        with open(SPLITS_CACHE_PATH, "rb") as f:
            cached_splits = pickle.load(f)
    else:
        print("No cached splits found, starting fresh")
        cached_splits = []

    if new_docs:
        print(f"Processing {len(new_docs)} new document(s)...")
        new_splits = []
        for doc_path in new_docs:
            doc_splits = split_single_document(doc_path)
            new_splits.extend(doc_splits)

        # Merge and save updated splits
        all_splits = cached_splits + new_splits
        with open(SPLITS_CACHE_PATH, "wb") as f:
            pickle.dump(all_splits, f)

        # Update JSON with newly processed files
        all_files = sorted(processed_files.union(new_docs))
        with open(DOCUMENTS_SPLITTED_PATH, "w", encoding="utf-8") as f:
            json.dump({"files": all_files}, f, indent=2)

        return all_splits
    else:
        print("No new documents to process.")
        return cached_splits


if __name__ == "__main__":
    print("Device:", device)
    embedding = embeddings(EMBEDDING_MODEL_PATH)
    print("Embedding model loaded:", embedding)
    documents = load_docs()
    splits = create_splits(documents)
    print(f"Total splits: {len(splits)}")
