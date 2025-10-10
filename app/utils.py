import markdown
from bs4 import BeautifulSoup, Tag
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from .models import DocumentSection
from . import db

model = OllamaLLM(model="llama3.2")
template = """Clean up the following section of Markdown/HTML while keeping formatting intact:" \
    
    Text: {text}
    
    Return cleaned content."""

prompt = PromptTemplate.from_template(template)
chain = prompt | model

def llm_cleanup_section(text: str) -> str:
    """
    Pass the section text to the LLM pipe and return cleaned content.
    """
    return chain.invoke({"text": text})

def markdown_to_sections2(md_text):

    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    soup = BeautifulSoup(html_body, "html.parser")

    sections = []
    header_tags = ["h1","h2","h3","h4","h5","h6"]
    current_section = None

    for node in soup.contents:
        if node.name in header_tags: # type: ignore
            if current_section:
                sections.append(current_section)
            current_section = {"header": str(node), "content": ""}
        else:
            if current_section:
                current_section["content"] += str(node)
            else:
                current_section = {"header": None, "content": str(node)}

    if current_section:
        sections.append(current_section)

    return sections

def upload_markdown_to_db(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Check if document already exists
    document_title = file_path.split("/")[-1]  # -> "test_doc.md"

    # Optionally remove the .md extension
    document_title = document_title.rsplit(".", 1)[0]

    sections = markdown_to_sections2(md_text)

    existing_sections = DocumentSection.query.filter_by(document_title=document_title).first()
    if existing_sections:
        print(f"Document '{document_title}' already exists in DB. Skipping upload.")
        return False

    # Push sections to DB
    for idx, sec in enumerate(sections):
        section_record = DocumentSection(document_title=document_title, position=idx,header=sec.get("header", ""), content=sec.get("content", "")) # type: ignore
        db.session.add(section_record)

    db.session.commit()
    print(f"Document '{document_title}' uploaded successfully with {len(sections)} sections.")
    return True

if __name__ == "__main__":
    path = "app/markdown/test_doc.md"

    upload_markdown_to_db(path)

    