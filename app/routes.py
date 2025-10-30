from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from io import BytesIO
import markdown
from .ai_func_rag import AIFunctionsOllamaLocal
from . import db
from .models import Documents, AIInteractions 
from .utils import html_to_docx, markdown_to_sections
from flask import session

main = Blueprint('main', __name__)

ai = AIFunctionsOllamaLocal()

@main.route('/content/<int:doc_id>')
@login_required
def content_generator_page(doc_id):
    document = Documents.query.filter_by(id=doc_id, user_id=current_user.id).first()
    
    if not document:
        # Return 404 if document not found or doesn't belong to user
        abort(404)
    return render_template('content_generator.html', document=document, loaded_content=document.content)

@main.route('/new_document', methods=['POST'])
@login_required
def new_document():
    doc_name = request.form.get('document_name')
    if not doc_name:
        flash("Please provide a document name", "warning")
        return redirect(url_for('main.dashboard'))  # or wherever your dashboard is

    # Check if a document with the same name already exists
    existing_doc = Documents.query.filter_by(document_name=doc_name).first()
    if existing_doc:
        flash("Document already exists. Opening it.", "info")
        document_id = existing_doc.id
    else:
        # Create a new document with the current user's ID
        new_doc = Documents(document_name=doc_name,  user_id=current_user.id) # type: ignore
        db.session.add(new_doc)
        db.session.commit()
        document_id = new_doc.id
        flash("New document created successfully!", "success")

    return redirect(url_for('main.content_generator_page', doc_id=document_id))



@main.route('/content_generation', methods=['POST'])
def generating_content():
    try:
        data = request.get_json()
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing prompt"}), 400

        prompt_text = data["prompt"]

        # create the human interaction
        human_interaction = AIInteractions(role="human", content=prompt_text, user_id=current_user.id if current_user.is_authenticated else None) # type: ignore

        # get AI response
        ai_response = ai.api_call(prompt_text)

        # create the AI interaction
        ai_interaction = AIInteractions(role="ai", content=ai_response,user_id=None)  # type: ignore # AI doesn't have a user

        # add both to session and commit once
        db.session.add_all([human_interaction, ai_interaction])
        db.session.commit()

        return jsonify({"output": ai_response})

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

@main.route('/dashboard/<username>')
@login_required
def dashboard(username):
    # Ensure the logged-in user is viewing their own dashboard
    if username != current_user.username:
        flash("You can only view your own dashboard.", "warning")
        return redirect(url_for('main.dashboard', username=current_user.username))

    # Query all documents created by this user
    user_docs = Documents.query.filter_by(user_id=current_user.id).order_by(Documents.date_created.desc()).all()
    
    return render_template('dashboard.html', user_docs=user_docs)

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