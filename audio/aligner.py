# audio/aligner.py
import uuid, subprocess, os
from flask import request, jsonify, send_from_directory, make_response

def run_alignment(request):
    if "audio" not in request.files:
        return jsonify(error="Missing required audio file."), 400
    audio_file = request.files["audio"]

    if "transcript" not in request.form:
        return jsonify(error="Missing transcript."), 400
    transcript = request.form["transcript"]

    lang = request.form.get("language", "english_mfa")
    response_mode = request.form.get("response", "file")

    if not audio_file.filename.lower().endswith((".wav", ".mp3")):
        return jsonify(error="Unsupported audio format. Please upload a .wav or .mp3 file."), 400

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
        return make_response(jsonify({
            "error": "MFA alignment failed",
            "message": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500)

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
