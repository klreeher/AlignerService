from flask import Flask, request, jsonify, send_from_directory, make_response
import uuid, subprocess, os, datetime
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

BUILD_TIME = datetime.datetime.utcnow().isoformat() + "Z"
try:
    GIT_COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
except Exception:
    GIT_COMMIT = "unknown"

@app.route("/align", methods=["POST"])
def align():
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
    audio_file = request.files["audio"]
    transcript = request.form["transcript"]
    lang = request.form.get("language", "english_mfa")
    response_mode = request.form.get("response", "file")  # "file" or "json"

    # File extension check
    if not audio_file.filename.lower().endswith((".wav", ".mp3")):
        return jsonify(error="Unsupported audio format. Please upload a .wav or .mp3 file."), 400

    # Ensure models are downloaded
    try:
        subprocess.run(["mfa", "model", "download", "dictionary", lang], check=True)
        subprocess.run(["mfa", "model", "download", "acoustic", lang], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Failed to download required MFA models",
            "message": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500

    job = str(uuid.uuid4())
    wd = f"/tmp/{job}"
    os.makedirs(f"{wd}/audio", exist_ok=True)

    audio_path = f"{wd}/audio/input.wav"
    lab_path = f"{wd}/audio/input.lab"

    audio_file.save(audio_path)
    with open(lab_path, "w") as f:
        f.write(transcript)

    out = f"{wd}/aligned"
    try:
        result = subprocess.run([
            "mfa", "align",
            f"{wd}/audio", lang, lang, out
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        response = make_response(jsonify({
            "error": "MFA alignment failed",
            "message": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    tg_path = os.path.join(out, "input.TextGrid")

    if response_mode == "json":
        try:
            with open(tg_path, "r") as f:
                textgrid_content = f.read()
            return jsonify({
                "filename": "input.TextGrid",
                "content": textgrid_content
            })
        except Exception as e:
            return jsonify(error="Failed to read TextGrid file", message=str(e)), 500
    else:
        response = make_response(send_from_directory(directory=out, path="input.TextGrid", mimetype="text/plain"))
        response.headers["Content-Disposition"] = "attachment; filename=input.TextGrid"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

@app.route("/version", methods=["GET"])
def version():
    """
    Get service version info.
    ---
    responses:
      200:
        description: Version metadata
    """
    return jsonify({
        "service": "aligner-service",
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
    """
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
