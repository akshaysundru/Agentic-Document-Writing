from flask import Blueprint, render_template, request, jsonify, send_file
from io import BytesIO
import markdown
#from .ai_func import AIFunctions
from .ai_func_rag import AIFunctionsOllamaLocal
from .models import DocumentSection
from . import db
from .utils import html_to_docx

main = Blueprint('main', __name__)

#ai = AIFunctions()
ai = AIFunctionsOllamaLocal()

@main.route('/content')
def content_generator_page():
    return render_template('content_generator.html')

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