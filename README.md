# === README.md ===
# Montreal Forced Aligner Docker Service

## Build Docker image:
```bash
docker build -t mfa-service .
```

## Run Docker container:
```bash
docker run -it -p 5000:5000 mfa-service
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

Happy aligning! 🎧
