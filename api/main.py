from flask import Flask, request, jsonify
from flasgger import Swagger
import datetime, subprocess
from datetime import datetime, timezone
from audio.aligner import run_alignment

app = Flask(__name__)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Nete API",
        "description": "Generate media-rich EPUBs from text, audio, and metadata",
        "version": "0.1.0"
    },
    "basePath": "/",
    "schemes": ["http"]
})

BUILD_TIME = datetime.now(timezone.utc).isoformat()

try:
    GIT_COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
except Exception:
    GIT_COMMIT = "unknown"

@app.route("/text/parse", methods=["POST"])
def text_parse():
    """
    Convert plain text and metadata into structured XHTML and internal JSON.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: text
        type: file
        required: true
      - in: formData
        name: metadata
        type: file
        required: true
    responses:
      200:
        description: Structured output
        schema:
          type: object
          properties:
            structured_text:
              type: string
            xhtml_files:
              type: array
              items:
                type: string
      501:
        description: Not yet implemented
    """
    return jsonify({"message": "text parsing not implemented yet"}), 501

@app.route("/assets/cover", methods=["POST"])
def assets_cover():
    """
    Upload or generate a cover image based on metadata.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: image
        type: file
        required: false
      - in: formData
        name: metadata
        type: file
        required: false
    responses:
      200:
        description: Cover image returned
        schema:
          type: object
          properties:
            cover_file:
              type: string
      501:
        description: Not yet implemented
    """
    return jsonify({"message": "cover generation not implemented yet"}), 501

@app.route("/epub", methods=["POST"])
def epub_build():
    """
    Assemble a final EPUB package from input files and metadata.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: metadata
        type: file
        required: true
      - in: formData
        name: xhtml_files
        type: file
        required: true
        description: XHTML files (can be multiple)
      - in: formData
        name: smil_files
        type: file
        required: false
      - in: formData
        name: cover
        type: file
        required: false
      - in: formData
        name: css
        type: file
        required: false
      - in: formData
        name: fonts
        type: file
        required: false
    responses:
      200:
        description: EPUB built successfully
        schema:
          type: object
          properties:
            epub_file:
              type: string
            log:
              type: string
            validation:
              type: object
              properties:
                epubcheck:
                  type: string
      501:
        description: Not yet implemented
    """
    return jsonify({"message": "epub builder not implemented yet"}), 501

@app.route("/audio/align", methods=["POST"])
def audio_align():
    """
    Align audio and transcript using Montreal Forced Aligner.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: audio
        type: file
        required: true
      - in: formData
        name: transcript
        type: string
        required: true
      - in: formData
        name: language
        type: string
        required: false
        default: english_mfa
      - in: formData
        name: response
        type: string
        enum: [json, file]
        default: file
    responses:
      200:
        description: Aligned TextGrid content or file
      400:
        description: Invalid input format
      500:
        description: Alignment or model error
    """
    return run_alignment(request)

@app.route("/version", methods=["GET"])
def version():
    """
    Get service version info.
    ---
    responses:
      200:
        description: Version metadata
        schema:
          type: object
          properties:
            service:
              type: string
            version:
              type: string
            mfa:
              type: string
            build_time:
              type: string
            git_commit:
              type: string
    """
    return jsonify({
        "service": "nete-audio",
        "version": "1.0.0",
        "mfa": "prebuilt-container",
        "build_time": BUILD_TIME,
        "git_commit": GIT_COMMIT
    })

@app.route("/healthz", methods=["GET"])
def healthcheck():
    """
    Health check endpoint.
    ---
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
    """
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
