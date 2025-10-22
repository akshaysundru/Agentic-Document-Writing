import os
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from .utils_vectorstore_retrievers import get_retrievers

class AIFunctionsOllamaLocal:
    def __init__(self):
        self.model = OllamaLLM(model="qwen3:30b")
        self.error = None
        self.retriever = get_retrievers()
        
    def retrieve_information(self, text: str):
        """Invoking the retriever based on the user question to return the most relevant information."""
        return self.retriever.invoke(text)
    
    def _generate(self, text: str, prompt_template: str):
        try:
            prompt = PromptTemplate.from_template(prompt_template)
            chain = prompt | self.model
            response = chain.invoke({"text": text})
            return response
        except Exception as e:
            return f"ERROR during generation: {e}"
                                
    def api_call(self, text: str) -> str:
        """Main RAG-based content generation pipeline."""
        try:
            retrieved_docs = self.retrieve_information(text)

            # Step 2: Debug print retrieved docs
            if not retrieved_docs:
                print("No documents retrieved.")
            else:
                for i, doc in enumerate(retrieved_docs):
                    print(f"Doc {i+1}:")
                    print(doc.page_content[:500])  # print first 500 chars to keep it readable
                    print("---")

            if not retrieved_docs:
                relevant_info = "No relevant documents found."
            else:
                relevant_info = "\n\n".join([doc.page_content for doc in retrieved_docs])

            content_generation = f"""
            You are an AI assistant with access to a set of retrieved documents.
            
            Context from retrieved documents:
            {relevant_info}

            User input:
            {text}

            Please generate content in accordance with the user input,
            making full use of the provided context. 
            
            Return only the final rewritten text, formatted with <br> tags where a new paragraph should start.
            """

            return self._generate(text=text, prompt_template=content_generation)

        except Exception as e:
            return f"ERROR during api_call: {e}"

