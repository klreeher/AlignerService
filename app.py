from flask import Flask, request, jsonify, send_from_directory
import uuid, subprocess, os

app = Flask(__name__)

@app.route("/align", methods=["POST"])
def align():
    audio_file = request.files["audio"]
    transcript = request.form["transcript"]
    lang = request.form.get("language", "english")

    job = str(uuid.uuid4())
    wd = f"/tmp/{job}"
    os.makedirs(f"{wd}/audio", exist_ok=True)
    os.makedirs(f"{wd}/text", exist_ok=True)

    audio_path = f"{wd}/audio/input.wav"
    text_path = f"{wd}/text/input.txt"

    audio_file.save(audio_path)
    with open(text_path, "w") as f:
        f.write(transcript)

    out = f"{wd}/aligned"
    try:
        subprocess.run([
            "mfa", "align",
            f"{wd}/audio", f"{wd}/text",
            lang, out
        ], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify(error=str(e)), 500

    # Assuming TextGrid output
    tg = os.path.join(out, "input.TextGrid")
    return send_from_directory(directory=out, path="input.TextGrid", mimetype="text/plain")
