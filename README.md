# Asset Flow

This is lightweight **REST API** built with [FastAPI](https://fastapi.tiangolo.com/) for converting file formats and optimizing images.

> Convert **CSV ↔ JSON** in one request. Compress **JPG/PNG - WebP** for up to 70 %+ file-size savings.

---

## Features

| Feature | Description |
|---------|-------------|
| **CSV - JSON** | Upload a CSV file and receive a structured JSON array |
| **JSON - CSV** | Upload a JSON array of objects and download a CSV file |
| **Image - WebP** | Convert JPEG/PNG images to WebP with configurable quality |
| **Auto Docs** | Interactive Swagger UI & ReDoc generated automatically |
| **Validation** | File-type, file-size, and content validation with clear error messages |
| **CORS Ready** | Pre-configured Cross-Origin Resource Sharing for frontend integration |

---

## Tech Stack

- **[Python 3.13.12](https://python.org)** - Modern Python with type hints
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance async web framework
- **[Pydantic v2](https://docs.pydantic.dev/)** - Data validation and settings management
- **[Pillow](https://python-pillow.org/)** - Image processing (JPG/PNG - WebP)
- **[Uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server
- **[pytest](https://pytest.org/)** - Testing framework

---

## Quick Start

### Prerequisites

- Python **3.10** or higher
- pip (comes with Python)

### 1 · Clone the repository

```bash
git clone https://github.com/WisdomEhirim06/asset-flow.git
cd asset-flow
```

### 2 · Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 · Install dependencies

```bash
pip install fastapi uvicorn[standard] python-multipart Pillow pydantic-settings
```

### 4 · (Optional) Configure environment variables

```bash
cp .env.example .env
# Edit .env to customize MAX_FILE_SIZE_MB, WEBP_QUALITY, etc.
```

### 5 · Start the server

```bash
uvicorn app.main:app --reload
```

The API is now running at **http://localhost:8000**.

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI (interactive API explorer) |
| http://localhost:8000/redoc | ReDoc (alternative documentation) |
| http://localhost:8000/health | Health-check endpoint |

---

## API Reference

### Health Check

```
GET /health
```

**Response** `200 OK`

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Convert CSV to JSON

```
POST /api/v1/convert/csv-to-json
```

Upload a `.csv` file and receive a JSON array of objects.

**Request** - `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | A `.csv` file |

**Example** using `curl`:

```bash
curl -X POST http://localhost:8000/api/v1/convert/csv-to-json \
  -F "file=@data.csv"
```

**Response** `200 OK`

```json
{
  "message": "CSV converted to JSON successfully",
  "original_filename": "data.csv",
  "record_count": 3,
  "data": [
    { "name": "Alice", "age": "30", "city": "NYC" },
    { "name": "Bob", "age": "25", "city": "LA" },
    { "name": "Charlie", "age": "35", "city": "Chicago" }
  ]
}
```

---

### Convert JSON to CSV

```
POST /api/v1/convert/json-to-csv
```

Upload a `.json` file containing an array of objects and download a CSV.

**Request** - `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | A `.json` file (array of objects) |

**Example** using `curl`:

```bash
curl -X POST http://localhost:8000/api/v1/convert/json-to-csv \
  -F "file=@data.json" \
  -o converted.csv
```

**Response** `200 OK` - A downloadable CSV file.

```
name,age,city
Alice,30,NYC
Bob,25,LA
Charlie,35,Chicago
```

---

### Convert Image to WebP

```
POST /api/v1/convert/image-to-webp
```

Upload a JPEG or PNG image and receive an optimized WebP version.

**Request** - `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | A `.jpg`, `.jpeg`, or `.png` image |

**Example** using `curl`:

```bash
curl -X POST http://localhost:8000/api/v1/convert/image-to-webp \
  -F "file=@photo.jpg" \
  -o photo.webp
```

**Response** `200 OK` - A downloadable `.webp` image.

Conversion metadata is included in the `X-Conversion-Meta` response header:

```json
{
  "original_filename": "photo.jpg",
  "original_format": "JPEG",
  "original_size_kb": 1024.0,
  "converted_size_kb": 310.5,
  "savings_percent": 69.7,
  "width": 1920,
  "height": 1080
}
```

---

### Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Unsupported file extension '.txt'. Allowed: .csv."
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Invalid file type or content |
| `413` | File exceeds size limit |
| `422` | Conversion failed (e.g., malformed data) |

---

## Running Tests

Install dev dependencies and run the test suite:

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## Project Structure

```
asset-flow/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # Environment-based settings
│   ├── schemas.py            # Pydantic response models
│   ├── exceptions.py         # Custom exceptions & handlers
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py         # GET /health
│   │   └── convert.py        # POST /api/v1/convert/*
│   └── services/
│       ├── __init__.py
│       ├── csv_json.py       # CSV ↔ JSON logic
│       └── image.py          # Image → WebP logic
├── tests/
│   ├── __init__.py
│   ├── test_csv_json.py      # CSV/JSON unit tests
│   ├── test_image.py         # Image conversion unit tests
│   └── test_api.py           # API integration tests
├── .env.example              # Environment variable template
├── .gitignore
├── pyproject.toml            # Project metadata & dependencies
└── README.md
```

---

## Configuration

All settings can be overridden via environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size in MB |
| `WEBP_QUALITY` | `80` | WebP output quality (1–100) |
| `ALLOWED_ORIGINS` | `localhost` | Comma-separated CORS origins |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "Add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
