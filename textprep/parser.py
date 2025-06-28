# textprep/parser.py

import os
import json
from uuid import uuid4
from flask import request, jsonify, render_template
from pydantic import ValidationError
from api.models.metadata import Metadata

# --- Utility: Split plain text into paragraphs + fragments ---
def parse_plain_text_to_paragraphs(text: str):
    """
    Splits plain text into paragraphs.
    Each paragraph can contain one or more fragments.
    For now: one fragment per paragraph.
    """
    raw_paragraphs = text.strip().split("\n\n")
    paragraphs = []

    for para in raw_paragraphs:
        # Clean up extra whitespace inside
        cleaned = " ".join(para.strip().splitlines()).strip()
        if cleaned:
            fragment = {"id": str(uuid4()), "text": cleaned}
            paragraphs.append([fragment])

    return paragraphs


# --- Main handler ---
def parse_text_and_metadata(request):
    if "text" not in request.files:
        return jsonify(error="Missing required text file."), 400
    if "metadata" not in request.files:
        return jsonify(error="Missing metadata file."), 400

    # Support single or multiple text files
    text_files = request.files.getlist("text")
    if not text_files:
        return jsonify(error="No text files found."), 400

    texts = []
    for tf in text_files:
        content = tf.read().decode("utf-8").strip()
        if not content:
            return jsonify(error="Empty text file."), 400
        texts.append(content)

    # Parse metadata
    metadata_file = request.files["metadata"]
    try:
        raw_metadata = json.load(metadata_file)
        metadata = Metadata(**raw_metadata)
    except json.JSONDecodeError as e:
        return jsonify(error="Invalid JSON in metadata", message=str(e)), 400
    except ValidationError as e:
        return jsonify(error="Invalid metadata", details=e.errors()), 400

    # --- Render XHTML files ---
    output_files = []
    structured_chapters = []

    for index, text in enumerate(texts, start=1):
        paragraphs = parse_plain_text_to_paragraphs(text)

        heading = {
            "id": f"chapter-{index}",
            "text": f"Chapter {index}"
        }

        xhtml_content = render_template(
            "chapter.xhtml.j2",  # your real template file in templates/
            heading=heading,
            paragraphs=paragraphs
        )

        filename = f"chapter{index}.xhtml"
        output_path = os.path.join("/tmp", filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xhtml_content)

        output_files.append(filename)
        structured_chapters.append({
            "filename": filename,
            "title": heading["text"]
        })

    # --- Build response ---
    return jsonify({
        "structured_text": {
            "title": metadata.title,
            "chapters": structured_chapters
        },
        "xhtml_files": output_files,
        "parsed_metadata": metadata.model_dump(mode="json")
    }), 200
