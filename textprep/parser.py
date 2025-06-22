# textprep/parser.py

import json
from flask import request, jsonify

def parse_text_and_metadata(request):
    if "text" not in request.files:
        return jsonify(error="Missing required text file."), 400
    if "metadata" not in request.files:
        return jsonify(error="Missing metadata file."), 400

    text_file = request.files["text"]
    metadata_file = request.files["metadata"]

    try:
        text_content = text_file.read().decode("utf-8")
    except Exception as e:
        return jsonify(error="Unable to read text file", message=str(e)), 400

    try:
        metadata = json.load(metadata_file)
    except json.JSONDecodeError as e:
        return jsonify(error="Invalid JSON in metadata", message=str(e)), 400

    # TODO: parse the text into structured format and XHTMLs
    # Placeholder output
    return jsonify({
        "structured_text": "structured_text.json",
        "xhtml_files": ["chapter1.xhtml", "chapter2.xhtml"]
    })
