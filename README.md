
# NETE - Media-Rich EPUB Generation API

**Nete** is a modular API service for generating **media-rich EPUB 3** files from plain text, metadata, and audio.  
Inspired by the Boeotian muse of melody and voice, Nete brings together text processing, audio alignment, and EPUB packaging into a fully automated publishing pipeline.

---

## Features

- Converts plain text into semantic XHTML chapters
- Aligns audio files to structured text to produce SMIL overlays
- Supports cover generation from metadata or custom images
- Assembles standards-compliant EPUB 3 files (with navigation, spine, assets)

---

## Project Structure

```
nete/
├── audio/         # Audio aligner + SMIL generator
├── textprep/      # Plain text → structured XHTML
├── assets/        # Cover generation, fonts, CSS
├── builder/       # EPUB assembly logic
├── api/           # REST API (Flask app, routes)
├── jobs/          # (Future) job orchestration + queuing
├── schemas/       # Pydantic models for API validation
├── data/          # Sample files, input/output artifacts
├── tests/         # Unit and integration tests
├── openapi/       # OpenAPI YAML spec
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Docker installed & running

---

## 🐳 **Build Docker image**

```bash
docker build -t aligner-service .
```

---

## 🐳 **Run Docker container (with output bind mount)**

To save generated XHTML files to your local machine, bind `/tmp` to a local `output/` folder:

```bash
mkdir -p output

docker run -it --rm \
  -p 8000:80 \
  -v $PWD/output:/tmp \
  aligner-service
```

✅ Now any XHTML files written to `/tmp` in the container will appear in your local `output/` folder.

Access the API at:  
**[http://localhost:8000/apidocs/](http://localhost:8000/apidocs/)**

---

## Example: Upload text + metadata for parsing

```bash
curl -X POST http://localhost:8000/text/parse \
  -F "text=@path/to/chapter1.txt" \
  -F "metadata=@path/to/metadata.json"
```

---

## Example Python client

```python
import requests

with open("chapter1.txt", "rb") as f:
    text_data = f.read()

metadata = {
    "title": "Example Book",
    "author": "Jane Doe"
}

import json
meta_bytes = json.dumps(metadata).encode("utf-8")

res = requests.post(
    "http://localhost:8000/text/parse",
    files={
        "text": ("chapter1.txt", text_data),
        "metadata": ("metadata.json", meta_bytes)
    }
)
print(res.json())
```

---

## Audio alignment example

```python
import requests

with open("sample.wav", "rb") as f:
    audio_data = f.read()

res = requests.post(
    "http://localhost:8000/audio/align",
    data={"transcript": "This is a test."},
    files={"audio": ("sample.wav", audio_data)}
)
print(res.text)
```

---

## Output

- `/text/parse` writes your structured XHTML to `./output/` on your host.
- `/audio/align` returns a TextGrid with aligned timing data.

---

## API Docs

Swagger UI:  
**[http://localhost:8000/apidocs/](http://localhost:8000/apidocs/)**

---

**Happy aligning & EPUB building!** 📚✨
