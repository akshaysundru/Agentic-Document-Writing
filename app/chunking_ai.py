from ollama import Client
import json
import fitz

NGROK_URL = "https://8bc99aa799dd.ngrok-free.app"

# Connect to Ollama server running on Kaggle
client = Client(host=NGROK_URL)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

import json

class DocumentAgent:
    def __init__(self, model, client):
        self.model = model
        self.client = client
        self.history = [
            {"role": "system", "content": """
You are an AI document assistant.
- Split documents into semantic chunks based on text headings.
- Return JSON arrays: {"title": "...", "text": "..."} for each chunk.
- Do not invent content.
- Respond in JSON only.
"""}
        ]

    def add_user_message(self, message_text):
        self.history.append({"role": "user", "content": message_text})

    def add_assistant_message(self, message_text):
        self.history.append({"role": "assistant", "content": message_text})

    def chat(self):
        # Call the model with full history
        response = self.client.chat(model=self.model, messages=self.history)
        output_text = response.message.content

        # Add assistant response to history
        self.add_assistant_message(output_text)
        return output_text

    def chunk_document(self, document_text):
        self.add_user_message(document_text)
        output = self.chat()
        try:
            chunks = json.loads(output)
        except json.JSONDecodeError:
            print("Failed to parse JSON. Raw output:")
            print(output)
            raise
        return chunks

if __name__ == "__main__":
    # Path to your PDF
    pdf_path = "/Users/akshaysundru2004/Desktop/Year 4/RAG-Project/pdf_folder/ENSC3016 Study Guide 1-Review of Circuit Fundamentals.pdf"

    # Extract text
    doc_text = extract_text_from_pdf(pdf_path)

    agent = DocumentAgent(model="qwen3:4b", client=client)

    # First, chunk the document
    chunks = agent.chunk_document(doc_text)

    # Then ask follow-up questions
    agent.add_user_message("Summarize the first two chunks.")
    summary = agent.chat()
    print(summary)