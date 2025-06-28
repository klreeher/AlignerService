# tests/test_models.py

import pytest
from pydantic import ValidationError
from api.models.metadata import Metadata

def test_metadata_valid_required_fields_only():
    data = {
        "title": "Test Book",
        "author": "Test Author"
    }
    m = Metadata(**data)
    assert m.title == "Test Book"
    assert m.author == "Test Author"
    assert m.subtitle is None  # Optional field should be None by default

def test_metadata_valid_all_fields():
    data = {
        "title": "Test Book",
        "subtitle": "Test Subtitle",
        "author": "Test Author",
        "description": "Some description",
        "narrator": "Narrator Name",
        "contributor": "Contributor Name",
        "original_url": "http://example.com",
        "fandom": "Example Fandom",
        "publisher": "Example Publisher"
    }
    m = Metadata(**data)
    assert str(m.original_url) == "http://example.com/"

def test_metadata_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        Metadata()
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('title',) for e in errors)
    assert any(e['loc'] == ('author',) for e in errors)

def test_metadata_invalid_url():
    bad_data = {
        "title": "Test",
        "author": "Author",
        "original_url": "not-a-valid-url"
    }
    with pytest.raises(ValidationError) as exc_info:
        Metadata(**bad_data)
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('original_url',) for e in errors)
