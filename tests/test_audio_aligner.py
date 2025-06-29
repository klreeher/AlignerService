import io
import os
import subprocess
import pytest

from api.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestAudioAligner:

    @pytest.mark.parametrize(
        "audio_filename,audio_bytes,response_mode,textgrid_content",
        [
            ("input.wav", b"fake-wav-data", None, "Fake TextGrid content"),
            ("input.mp3", b"fake-mp3-data", None, "Fake TextGrid content"),
            ("input.wav", b"fake-wav", "json", "Fake TextGrid JSON"),
        ]
    )
    def test_audio_aligner(
        self, client, monkeypatch, tmp_path,
        audio_filename, audio_bytes, response_mode, textgrid_content
    ):
        """Parametrized test: WAV, MP3, JSON inline mode"""
        monkeypatch.setenv("ARTIFACT_DIR", str(tmp_path))  # ✅ Provide the env var!

        monkeypatch.setattr(
            "audio.aligner.subprocess.run",
            lambda *a, **k: subprocess.CompletedProcess(a[0], 0)
        )
        monkeypatch.setattr("audio.aligner.uuid.uuid4", lambda: "testjob")
        monkeypatch.setattr("audio.aligner.os.makedirs", lambda *a, **k: None)
        monkeypatch.setattr("audio.aligner.os.path.exists", lambda path: True)

        # Create fake output dir
        aligned_dir = tmp_path / "testjob" / "aligned"
        aligned_dir.mkdir(parents=True, exist_ok=True)
        textgrid_path = aligned_dir / "input.TextGrid"
        textgrid_path.write_text(textgrid_content)

        # ✅ Pre-create the *input* audio dir too!
        audio_dir = tmp_path / "testjob" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Patch join only for output
        real_join = os.path.join
        def fake_join(*a):
            if "aligned" in a:
                return str(textgrid_path)
            return real_join(*a)
        monkeypatch.setattr("audio.aligner.os.path.join", fake_join)

        data = {
            "audio": (io.BytesIO(audio_bytes), audio_filename),
            "transcript": "Example transcript"
        }
        if response_mode:
            data["response"] = response_mode

        response = client.post("/audio/align", data=data, content_type="multipart/form-data")
        assert response.status_code == 200

    def test_missing_textgrid_after_success(self, monkeypatch, client, tmp_path):
        """Should 500 if alignment runs but TextGrid is missing"""
        monkeypatch.setenv("ARTIFACT_DIR", str(tmp_path))  # ✅
        monkeypatch.setattr(
            "audio.aligner.subprocess.run",
            lambda *a, **k: subprocess.CompletedProcess(a[0], 0)
        )
        monkeypatch.setattr("audio.aligner.uuid.uuid4", lambda: "testjob")
        monkeypatch.setattr("audio.aligner.os.makedirs", lambda *a, **k: None)
        monkeypatch.setattr("audio.aligner.os.path.exists", lambda path: False)

        # ✅ Pre-create audio dir for input file save
        audio_dir = tmp_path / "testjob" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "audio": (io.BytesIO(b"fake-wav"), "input.wav"),
            "transcript": "text"
        }
        response = client.post("/audio/align", data=data, content_type="multipart/form-data")
        assert response.status_code == 500
        assert "TextGrid" in response.get_data(as_text=True)

    def test_invalid_audio_format(self, client):
        """Should return 400 for unsupported audio format"""
        data = {
            "audio": (io.BytesIO(b"fake-data"), "input.xyz"),
            "transcript": "test"
        }
        response = client.post("/audio/align", data=data, content_type="multipart/form-data")
        assert response.status_code == 400

    def test_alignment_subprocess_error(self, monkeypatch, client, tmp_path):
        """Should 500 if subprocess fails"""
        monkeypatch.setenv("ARTIFACT_DIR", str(tmp_path))  # ✅
        monkeypatch.setattr(
            "audio.aligner.subprocess.run",
            lambda *a, **k: subprocess.CompletedProcess(a[0], 1)
        )
        monkeypatch.setattr("audio.aligner.uuid.uuid4", lambda: "testjob")

        # ✅ Pre-create audio dir for input file save
        audio_dir = tmp_path / "testjob" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "audio": (io.BytesIO(b"fake-wav"), "input.wav"),
            "transcript": "text"
        }
        response = client.post("/audio/align", data=data, content_type="multipart/form-data")
        assert response.status_code == 500
