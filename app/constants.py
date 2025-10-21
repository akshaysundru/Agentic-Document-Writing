from langchain_ollama import OllamaLLM
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # one level up from Pipeline/

SPLITS_CACHE_PATH = os.path.join(PROJECT_ROOT, "app", "cache", "splits_cache.pkl")
PDF_DIR = os.path.join(PROJECT_ROOT, "app", "confidential_documents")
EMBEDDING_MODEL_PATH = os.path.join(PROJECT_ROOT, "local_models/all-MiniLM-L6-v2")
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "faiss_index")
BM25_CACHE_PATH = os.path.join(PROJECT_ROOT, "app", "cache", "bm25_cache.pkl")
DOCUMENTS_SPLITTED_PATH = os.path.join(PROJECT_ROOT, "app", "cache", "processed_docs.json")

MODEL_NAME = "llama3.2"
llm = OllamaLLM(model = MODEL_NAME)

if __name__ == "__main__":
    print(PROJECT_ROOT)
    print(PDF_DIR)
    print(EMBEDDING_MODEL_PATH)
    print(SPLITS_CACHE_PATH) #these files should verify the paths outputted match what we require