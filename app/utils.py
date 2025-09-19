import markdown
from bs4 import BeautifulSoup, Tag
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from .models import DocumentSection
from . import db

def markdown_to_sections(md_text):
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    soup = BeautifulSoup(html_body, "html.parser")

    sections = []
    current_section = None

    for node in soup.children:
        if isinstance(node, str):
            continue  # ignore plain text nodes
        if node.name and node.name.startswith('h') and node.name[1].isdigit():
            # Save previous section
            if current_section:
                sections.append(current_section)
            # New header section
            current_section = {"header": node.get_text(), "content": str(node)}
        else:
            if current_section:
                current_section["content"] += str(node)
            else:
                # Content before first header
                current_section = {"header": None, "content": str(node)}

    if current_section:
        sections.append(current_section)

    return sections


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