from flask import Blueprint, render_template, request, jsonify, flash
from .utils import markdown_to_sections2, upload_markdown_to_db
import markdown
from .ai_func import AIFunctions
from .models import DocumentSection
from . import db

main = Blueprint('main', __name__)

ai = AIFunctions()

@main.route('/docs')
def document2():
    # Check if DB already has sections
    db_sections = DocumentSection.query.order_by(DocumentSection.position).all()

    if not db_sections:  # first load, DB empty → seed from markdown
        upload_markdown_to_db("app/markdown/test_doc.md")

    db_sections = DocumentSection.query.order_by(DocumentSection.position).all()
    document_title = db_sections[0].document_title if db_sections else None

    return render_template("document.html", sections=db_sections, title = document_title)

@main.route("/clean_section", methods=["POST"])
def clean_section():
    data = request.get_json(silent=False)
    if not data or "html" not in data or "position" not in data:
        return jsonify({"ok": False, "error": "No HTML or position received"}), 400

    html = data["html"]
    position = data.get("position")
    if position is None:
        return jsonify({"ok": False, "error": "Position is None"}), 400

    try:
        position = int(position)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid position"}), 400

    # Call your AI clean function
    cleaned_html = ai.clean_text(html)
    print("Cleaned HTML:", cleaned_html)

    # Update the DB section and commit
    section = DocumentSection.query.filter_by(position=position).first()
    if section:
        section.content = cleaned_html
        db.session.commit()  # <-- ensures changes are saved to DB

    return jsonify({"ok": True, "cleaned_html": cleaned_html})

@main.route("/save", methods=["POST"])
def save_sections():
    data = request.get_json()
    sections = data.get("sections", [])

    for sec in sections:
        section = DocumentSection.query.get(sec["id"])
        if section:
            if sec.get("header") is not None:
                section.header = sec["header"]
            if sec.get("content") is not None:
                section.content = sec["content"]

    try:
        db.session.commit()
        return jsonify({"message": "Changes saved successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error saving: {e}"}), 500


