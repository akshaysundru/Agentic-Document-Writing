from flask import Blueprint, render_template, request, jsonify, flash
from .utils import markdown_to_sections, llm_cleanup_section
import markdown
from app.ai_func import clean_text
from .models import DocumentSection
from . import db

main = Blueprint('main', __name__)

@main.route('/document')
def document():
    with open("app/markdown/test_doc.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    sections = markdown_to_sections(md_text)

    # Save to DB if not already present
    existing = DocumentSection.query.count()
    if existing == 0:
        for pos, sec in enumerate(sections):
            db_sec = DocumentSection(
                header=sec["header"],
                content=sec["content"],
                position=pos
            )
            db.session.add(db_sec)
        db.session.commit()

    # Load from DB for rendering
    sections_html = []
    db_sections = DocumentSection.query.order_by(DocumentSection.position).all()
    for sec in db_sections:
        sections_html.append(f'<div class="editable-section" data-section-id="{sec.id}" contenteditable="true">{sec.content}</div>')

    return render_template("document.html", sections_html="".join(sections_html))


@main.route("/clean_section", methods=["POST"])
def clean_section():
    data = request.get_json(silent=True)
    if not data or "html" not in data:
        return jsonify({"ok": False, "error": "No HTML received"}), 400

    html = data["html"]
    cleaned_html = clean_text(html)  # your AI function
    return jsonify({"ok": True, "cleaned_html": cleaned_html})

