# === README.md ===
# NETE - Media-Rich EPUB Generation API

**Nete** is a modular API service for generating **media-rich EPUB 3** files from plain text, metadata, and audio. Inspired by the Boeotian muse of melody and voice, Nete brings together text processing, audio alignment, and EPUB packaging into a fully automated publishing pipeline.

## Features

- Converts plain text into semantic XHTML chapters
- Aligns audio files to structured text to produce SMIL overlays
- Supports cover generation from metadata or custom images
- Assembles standards-compliant EPUB 3 files (with navigation, spine, assets)


## Project Structure
  
nete/
├── audio/         
│   ├── aligner.py
│   ├── smil_generator.py      # Audio + text sync, SMIL generation
├── textprep/      # Plain text → structured XHTML
├── assets/        # Cover generation, fonts, CSS
├── builder/       # EPUB assembly logic
├── api/           # REST API (FastAPI app, routers)
├── jobs/          # (Future) job orchestration + queuing
├── schemas/       # Pydantic models for API validation
├── data/          # Sample files, input/output artifacts
├── tests/         # Unit and integration tests
├── openapi/       # OpenAPI YAML spec
└── README.md


# Quick Start

### Prerequisites
- Python 3.9+


## Build Docker image:
```bash
docker build -t aligner-service .
```

## Run Docker container:
```bash
docker run -it -p 5000:5000 aligner-service 
```

## Sample Request (Python):
```python
import requests

with open("sample.wav", "rb") as f:
    audio_data = f.read()

res = requests.post(
    "http://localhost:5000/align",
    data={"transcript": "This is a test."},
    files={"audio": ("sample.wav", audio_data)}
)
print(res.text)
```

## Sample Request (C#):
```csharp
using var client = new HttpClient();
using var form = new MultipartFormDataContent();
form.Add(new StringContent("This is a test."), "transcript");
form.Add(new StreamContent(File.OpenRead("sample.wav")), "audio", "sample.wav");
var response = await client.PostAsync("http://localhost:5000/align", form);
Console.WriteLine(await response.Content.ReadAsStringAsync());
```

---

## Output
Returns `input.TextGrid` containing aligned timing data.

---

## API Docs

http://172.17.0.2:5000/apidocs/

Happy aligning! 🎧
