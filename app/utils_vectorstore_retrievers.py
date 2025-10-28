import os
import faiss
import pickle
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from .constants import PDF_DIR, FAISS_INDEX_PATH, EMBEDDING_MODEL_PATH, BM25_CACHE_PATH
from .utils_embed_splitting import load_docs, create_splits, embeddings

def build_vector_store(embeddings, splits):
    dim = len(embeddings.embed_query("test sentence"))

    # FAISS CPU index only
    cpu_index = faiss.IndexFlatL2(dim)

    if os.path.exists(FAISS_INDEX_PATH):
        print("Loading FAISS index from disk...")
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("Building FAISS index from scratch...")
        vector_store = FAISS(
            embedding_function=embeddings,
            index=cpu_index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        vector_store.add_documents(splits)
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

    # Build vector store (CPU)
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
    ensemble_retriever, semantic_retriever, bm25_retriever = get_retrievers()
    print("Ensemble retriever:", ensemble_retriever)
    print("Semantic retriever:", semantic_retriever)
    print("BM25 retriever:", bm25_retriever)