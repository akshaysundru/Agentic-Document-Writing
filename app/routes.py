from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from io import BytesIO
import markdown
from .ai_func_rag import AIFunctionsOllamaLocal
from . import db
from .models import Documents, User
from .utils import html_to_docx, markdown_to_sections
from flask import session

main = Blueprint('main', __name__)

ai = AIFunctionsOllamaLocal()

@main.route('/content/<int:doc_id>')
@login_required
def content_generator_page(doc_id):
    document = Documents.query.get_or_404(doc_id)
    return render_template('content_generator.html', document=document, loaded_content=document.content)


@main.route('/new_document', methods=['POST'])
@login_required
def new_document():
    doc_name = request.form.get('document_name')
    if not doc_name:
        flash("Please provide a document name", "warning")
        return redirect(url_for('main.dashboard'))  # or wherever your dashboard is

    existing_doc = Documents.query.filter_by(document_name=doc_name).first()
    if existing_doc:
        flash("Document already exists. Opening it.", "info")
        document_id = existing_doc.id
    else:
        new_doc = Documents(document_name=doc_name)
        db.session.add(new_doc)
        db.session.commit()
        document_id = new_doc.id
        flash("New document created successfully!", "success")

    return redirect(url_for('main.content_generator_page', doc_id=document_id))


@main.route('/content_generation', methods=['POST'])
def generating_content():
    try:
        data = request.get_json()
        print("Received data:", data)

        if not data or "prompt" not in data:
            return jsonify({"error": "Missing prompt"}), 400

        text = data["prompt"]
        print("Prompt:", text)

        result = ai.api_call(text)
        print("Result:", result)

        return jsonify({"output": result})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@main.route('/content/<int:document_id>/save', methods=['POST']) 
@login_required 
def save_document(document_id): 
    data = request.get_json() 
    content = data.get("content", "") 
    document = Documents.query.get_or_404(document_id) 
    document.content = content 
    db.session.commit()
    return {"status": "success"}, 200


@main.route('/export_word', methods=['POST'])
def export_word():
    data = request.get_json()
    html_content = data.get('content', '')

    if not html_content:
        return jsonify({"error": "No content provided"}), 400

    file_stream = html_to_docx(html_content)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="generated_content.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main.route('/markdown_view', methods=['GET', 'POST'])
@login_required
def markdown_view():
    sections = []
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file and uploaded_file.filename.endswith('.md'): # type: ignore
            md_text = uploaded_file.read().decode('utf-8')
            sections = markdown_to_sections(md_text)
        else:
            flash('Please upload a valid Markdown (.md) file', 'danger')
            return redirect(url_for('main.markdown_view'))

    return render_template('markdown_view.html', sections=sections)


@main.route('/base')
def base():
    return render_template('base_navbar.html')