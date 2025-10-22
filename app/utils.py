from io import BytesIO
from docx import Document
from docx.shared import Pt
from flask import send_file
from bs4 import BeautifulSoup, Tag

def html_to_docx(html_content: str) -> BytesIO:
    """
    Converts simple HTML (paragraphs, <br>, tables) to a Word document in memory.
    """
    doc = Document()
    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup.contents:
        if isinstance(element, Tag):
            if element.name == "p":
                p = doc.add_paragraph()
                p.add_run(element.get_text(separator="\n")).font.size = Pt(12)
            elif element.name == "br":
                doc.add_paragraph()  # add line break as a new paragraph
            elif element.name == "table":
                rows = element.find_all("tr")
                if rows:
                    table = doc.add_table(rows=0, cols=len(rows[0].find_all(["td", "th"])))
                    for row in rows:
                        cells = row.find_all(["td", "th"])
                        row_cells = table.add_row().cells
                        for i, cell in enumerate(cells):
                            row_cells[i].text = cell.get_text()
        else:
            # For plain strings or other non-tag content, add as a paragraph
            text = str(element).strip()
            if text:
                doc.add_paragraph(text)

    # Save to in-memory file
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
