# api/main.py
from flask import Flask, request, jsonify
from flasgger import Swagger
import datetime, subprocess

from audio.aligner import run_alignment

app = Flask(__name__)
swagger = Swagger(app)

BUILD_TIME = datetime.datetime.utcnow().isoformat() + "Z"
try:
    GIT_COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
except Exception:
    GIT_COMMIT = "unknown"



@app.route("/text/parse", methods=["POST"])
def text_parse():
    """Stub: convert plain text to structured XHTML."""
    return jsonify({"message": "text parsing not implemented yet"}), 501

@app.route("/assets/cover", methods=["POST"])
def assets_cover():
    """Stub: upload or generate cover image."""
    return jsonify({"message": "cover generation not implemented yet"}), 501

@app.route("/epub", methods=["POST"])
def epub_build():
    """Stub: build final EPUB from components."""
    return jsonify({"message": "epub builder not implemented yet"}), 501

@app.route("/audio/align", methods=["POST"])
def audio_align():
    """Align audio and transcript using Montreal Forced Aligner.
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
    """Get service version info."""
    return jsonify({
        "service": "nete-audio",
        "version": "1.0.0",
        "mfa": "prebuilt-container",
        "build_time": BUILD_TIME,
        "git_commit": GIT_COMMIT
    })

@app.route("/healthz", methods=["GET"])
def healthcheck():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
