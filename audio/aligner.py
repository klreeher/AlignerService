import uuid
import subprocess
import os
from flask import request, jsonify, send_file, make_response


def run_alignment(request, artifact_dir="/tmp"):
    # Create a unique job directory under the artifact root
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(artifact_dir, job_id)
    audio_dir = os.path.join(job_dir, "audio")
    out_dir = os.path.join(job_dir, "aligned")

    os.makedirs(audio_dir, exist_ok=True)

    # Validate input
    if "audio" not in request.files:
        return jsonify(error="Missing required audio file."), 400
    audio_file = request.files["audio"]

    if "transcript" not in request.form:
        return jsonify(error="Missing transcript."), 400
    transcript = request.form["transcript"]

    lang = request.form.get("language", "english_mfa")
    response_mode = request.form.get("response", "file")

    # Validate audio format
    input_ext = os.path.splitext(audio_file.filename)[1].lower()
    if input_ext not in [".wav", ".mp3"]:
        return jsonify(error="Unsupported audio format. Please upload a .wav or .mp3 file."), 400

    # Download MFA models
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

    # Save audio and transcript
    input_path = os.path.join(audio_dir, f"input{input_ext}")
    wav_path = os.path.join(audio_dir, "input.wav")
    lab_path = os.path.join(audio_dir, "input.lab")

    audio_file.save(input_path)
    with open(lab_path, "w") as f:
        f.write(transcript)

    # Convert MP3 to WAV if needed
    if input_ext == ".mp3":
        try:
            subprocess.run([
                "ffmpeg", "-i", input_path,
                "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le",
                wav_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({
                "error": "Failed to convert MP3 to WAV",
                "message": str(e)
            }), 500
    else:
        wav_path = input_path  # Already WAV

    # Run MFA aligner
    try:
        subprocess.run(
            ["mfa", "align", audio_dir, lang, lang, out_dir],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
    except subprocess.CalledProcessError as e:
        return make_response(jsonify({
            "error": "MFA alignment failed",
            "message": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr
        }), 500)

    # Verify output TextGrid
    tg_filename = "input.TextGrid"
    tg_path = os.path.join(out_dir, tg_filename)
    if not os.path.exists(tg_path):
        return jsonify(error="Alignment finished but output TextGrid was not found."), 500

    result = {
        "job_id": job_id,
        "textgrid_file": tg_filename,
        "textgrid_path": tg_path
    }

    # Respond with JSON or file download
    if response_mode == "json":
        try:
            with open(tg_path, "r") as f:
                result["content"] = f.read()
        except Exception as e:
            return jsonify(error="Failed to read TextGrid file", message=str(e)), 500
        return jsonify(result), 200
    else:
        response = make_response(send_file(tg_path, mimetype="text/plain"))
        response.headers["Content-Disposition"] = f"attachment; filename={tg_filename}"
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["X-Job-Id"] = job_id
        return response
