import os
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from .constants import PDF_DIR, FAISS_INDEX_PATH, EMBEDDING_MODEL_PATH, BM25_CACHE_PATH
from .utils_embed_splitting import load_docs, create_splits, embeddings
import pickle
import torch


def build_vector_store(embeddings, splits):
    # Check whether GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Building FAISS index on {device.upper()}")

    dim = len(embeddings.embed_query("test sentence"))

    # --- Create base FAISS index ---
    cpu_index = faiss.IndexFlatL2(dim)

    # If GPU available, create GPU resources once
    gpu_res = None
    if device == "cuda":
        gpu_res = faiss.StandardGpuResources()

    # Load existing FAISS index if available
    if os.path.exists(FAISS_INDEX_PATH):
        print("Loading FAISS index from disk...")
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

        # Move FAISS index to GPU if applicable
        if device == "cuda":
            vector_store.index = faiss.index_cpu_to_gpu(gpu_res, 0, vector_store.index)

    else:
        print("Building FAISS index from scratch...")
        # Use GPU or CPU based on availability
        index = faiss.index_cpu_to_gpu(gpu_res, 0, cpu_index) if device == "cuda" else cpu_index

        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        vector_store.add_documents(splits)

        # Before saving, always convert back to CPU for portability
        if device == "cuda":
            vector_store.index = faiss.index_gpu_to_cpu(vector_store.index)
        vector_store.save_local(FAISS_INDEX_PATH)

    return vector_store

def get_bm25_retriever(splits, k=4):
    if os.path.exists(BM25_CACHE_PATH):
        print("Loading cached BM25 retriever from disk...")
        with open(BM25_CACHE_PATH, "rb") as f:
            bm25_retriever = pickle.load(f)
    else:
        print("Building new BM25 retriever...")
        bm25_retriever = BM25Retriever.from_documents(splits)
        bm25_retriever.k = k
        with open(BM25_CACHE_PATH, "wb") as f:
            pickle.dump(bm25_retriever, f)
    return bm25_retriever

def get_retrievers(pdf_folder=PDF_DIR, k=4):
    # Load documents and splits
    documents = load_docs(pdf_folder)
    embedding = embeddings(EMBEDDING_MODEL_PATH)
    splits = create_splits(documents)

    # Build vector store
    vector_store = build_vector_store(embedding, splits)

    # Create retrievers
    semantic_retriever = vector_store.as_retriever(search_kwargs={'k': k})
    bm25_retriever = get_bm25_retriever(splits)

    # Ensemble retriever
    ensemble_retriever = EnsembleRetriever(
        retrievers=[semantic_retriever, bm25_retriever],
        weights=[0.5, 0.5]
    )

    return ensemble_retriever

if __name__ == "__main__":
    ensemble_retriever = get_retrievers()
    print(ensemble_retriever)