import io
import pytest
from api.main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_text_parse_success(client):
    text = io.BytesIO(b"This is a test paragraph.")
    metadata = io.BytesIO(b'{"title": "Test Book"}')

    data = {
        "text": (text, "book.txt"),
        "metadata": (metadata, "metadata.json")
    }

    response = client.post("/text/parse", data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert "structured_text" in response.get_json()

def test_text_parse_missing_text(client):
    metadata = io.BytesIO(b'{"title": "Only metadata"}')
    data = {"metadata": (metadata, "metadata.json")}

    response = client.post("/text/parse", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert "Missing required text file" in response.get_data(as_text=True)
