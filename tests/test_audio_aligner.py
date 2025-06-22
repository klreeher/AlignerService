import io
import pytest
import subprocess

from api.main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_missing_audio(client):
    """Should return 400 when no audio is uploaded"""
    data = {
        "transcript": "This is a test sentence."
    }
    response = client.post("/audio/align", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert "Missing required audio file" in response.get_data(as_text=True)


def test_invalid_audio_format(client):
    """Should reject non-wav/mp3 files"""
    data = {
        "audio": (io.BytesIO(b"not-audio"), "test.txt"),
        "transcript": "Hello world"
    }
    response = client.post("/audio/align", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert "Unsupported audio format" in response.get_data(as_text=True)

def test_alignment_subprocess_failure(monkeypatch, client):
    """Should handle subprocess failures cleanly"""

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd=args[0], output="fail", stderr="nope")

    monkeypatch.setattr("audio.aligner.subprocess.run", fake_run)

    data = {
        "audio": (io.BytesIO(b"fake-wav-data"), "input.wav"),
        "transcript": "This is a test"
    }
    response = client.post("/audio/align", data=data, content_type='multipart/form-data')
    assert response.status_code == 500
    assert "Failed to download required MFA models" in response.get_data(as_text=True)
