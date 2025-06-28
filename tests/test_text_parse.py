import io
import pytest
import json
from api.main import app
from textprep import parser


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestTextParse:
    """Grouped tests for /text/parse endpoint."""

    def test_success_single_file(self, client):
        """Happy path: valid text and metadata produce 200 and JSON output."""
        text = io.BytesIO(b"This is a test paragraph.")
        json_meta = {
            "title": "Shang Qinghua's No Good Very Bad Several Iterations Of A Day",
            "subtitle": "(never eat an orange on the wrong holiday)",
            "author": "Asymptotical",
            "description": "Originally posted by Asymptotical on AO3, 2019 December 25.",
            "narrator": "Isweedan",
            "contributor": "Madecunningly",
            "original_url": "http://archiveofourown.org/works/21949045",
            "fandom": "人渣反派自救系统 - 墨香铜臭 | The Scum Villain's Self-Saving System - Mòxiāng Tóngxiù",
            "publisher": "made most cunningly"
        }
        metadata = io.BytesIO(json.dumps(json_meta).encode("utf-8"))
        data = {
            "text": (text, "book.txt"),
            "metadata": (metadata, "metadata.json")
        }
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
        assert "structured_text" in response.get_json()

    def test_success_multiple_files(self, client):
        """Valid multiple text files → multiple chapters in output."""
        text1 = io.BytesIO(b"Chapter 1: This is the first chapter.")
        text2 = io.BytesIO(b"Chapter 2: This is the second chapter.")
        json_meta = {"title": "Multi-Chapter Book", "author": "Test Author"}
        metadata = io.BytesIO(json.dumps(json_meta).encode("utf-8"))
        data = {
            "text": [(text1, "chapter1.txt"), (text2, "chapter2.txt")],
            "metadata": (metadata, "metadata.json")
        }
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
        json_data = response.get_json()
        assert "structured_text" in json_data
        assert len(json_data["structured_text"]["chapters"]) == 2

    def test_creates_real_xhtml_file(self, client, tmp_path, monkeypatch):
        """XHTML output is physically created, has content."""
        monkeypatch.setattr(parser, "DEFAULT_OUTPUT_DIR", tmp_path)
        text = io.BytesIO(b"This is a test paragraph.\n\nSecond para.")
        json_meta = {"title": "Book", "author": "Author"}
        metadata = io.BytesIO(json.dumps(json_meta).encode("utf-8"))
        data = {"text": (text, "book.txt"), "metadata": (metadata, "metadata.json")}
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
        json_out = response.get_json()
        files = json_out["xhtml_files"]
        assert len(files) == 1
        output_file = tmp_path / files[0]
        assert output_file.exists()
        contents = output_file.read_text(encoding="utf-8")
        assert "<section" in contents
        assert "<p>" in contents
        assert "This is a test paragraph." in contents
        assert "Second para." in contents
        assert "chapter-1" in contents

    def test_missing_text_file(self, client):
        """Error: no text uploaded → 400."""
        metadata = io.BytesIO(b'{"title": "Only metadata", "author": "T"}')
        data = {"metadata": (metadata, "metadata.json")}
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "Missing required text file" in response.get_data(as_text=True)

    def test_missing_metadata_file(self, client):
        """Error: no metadata uploaded → 400."""
        text = io.BytesIO(b"Hello world.")
        data = {"text": (text, "file.txt")}
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "Missing metadata file" in response.get_data(as_text=True)

    def test_invalid_json_metadata(self, client):
        """Error: metadata is not valid JSON → 400."""
        text = io.BytesIO(b"Hello world.")
        bad_metadata = io.BytesIO(b"This is not JSON")
        data = {"text": (text, "file.txt"), "metadata": (bad_metadata, "metadata.json")}
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "Invalid JSON" in response.get_data(as_text=True)

    def test_invalid_metadata_schema(self, client):
        """Error: metadata JSON is invalid against schema → 400."""
        text = io.BytesIO(b"Hello world.")
        bad_meta = {"title": "T", "author": "A", "original_url": "not-a-url"}
        bad_metadata = io.BytesIO(json.dumps(bad_meta).encode("utf-8"))
        data = {"text": (text, "file.txt"), "metadata": (bad_metadata, "metadata.json")}
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "Invalid metadata" in response.get_data(as_text=True)

    def test_single_empty_text_file(self, client):
        """Error: text file is empty → 400."""
        empty_text = io.BytesIO(b"")
        json_meta = {"title": "Empty File Book", "author": "Author"}
        metadata = io.BytesIO(json.dumps(json_meta).encode("utf-8"))
        data = {"text": (empty_text, "empty.txt"), "metadata": (metadata, "metadata.json")}
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "Empty text file" in response.get_data(as_text=True)

    def test_multiple_empty_text_files(self, client):
        """Error: all text files empty → 400."""
        empty1 = io.BytesIO(b"")
        empty2 = io.BytesIO(b"")
        json_meta = {"title": "Multiple Empty Files", "author": "Author"}
        metadata = io.BytesIO(json.dumps(json_meta).encode("utf-8"))
        data = {"text": [(empty1, "empty1.txt"), (empty2, "empty2.txt")], "metadata": (metadata, "metadata.json")}
        response = client.post("/text/parse", data=data, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "Empty text file" in response.get_data(as_text=True)

    def test_mixed_files_one_empty(self, client):
        """Error: mix of valid & empty files → 400."""
        valid = io.BytesIO(b"Valid text.")
        empty = io.BytesIO(b"")
        json_meta = {"title": "Mixed", "author": "A"}
        metadata = io.BytesIO(json.dumps(json_meta).encode("utf-8"))
        data = {
            "text": [(valid, "valid.txt"), (empty, "empty.txt")],
            "metadata": (metadata, "metadata.json")
        }
