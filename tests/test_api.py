"""Integration tests for the API endpoints using FastAPI TestClient."""

import io
import json

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "healthy"
        assert "version" in body


# ---------------------------------------------------------------------------
# CSV → JSON
# ---------------------------------------------------------------------------

class TestCsvToJson:
    def test_convert_csv(self):
        csv_content = b"name,age\nAlice,30\nBob,25\n"
        resp = client.post(
            "/api/v1/convert/csv-to-json",
            files={"file": ("data.csv", csv_content, "text/csv")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["record_count"] == 2
        assert body["data"][0]["name"] == "Alice"

    def test_reject_non_csv(self):
        resp = client.post(
            "/api/v1/convert/csv-to-json",
            files={"file": ("data.txt", b"hello", "text/plain")},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# JSON → CSV
# ---------------------------------------------------------------------------

class TestJsonToCsv:
    def test_convert_json(self):
        data = [{"name": "Alice", "age": 30}]
        resp = client.post(
            "/api/v1/convert/json-to-csv",
            files={"file": ("data.json", json.dumps(data).encode(), "application/json")},
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Alice" in resp.text

    def test_reject_non_json(self):
        resp = client.post(
            "/api/v1/convert/json-to-csv",
            files={"file": ("data.xml", b"<xml/>", "application/xml")},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Image → WebP
# ---------------------------------------------------------------------------

class TestImageToWebp:
    @staticmethod
    def _make_jpeg() -> bytes:
        img = Image.new("RGB", (80, 80), color="green")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return buf.getvalue()

    def test_convert_jpeg(self):
        jpeg = self._make_jpeg()
        resp = client.post(
            "/api/v1/convert/image-to-webp",
            files={"file": ("photo.jpg", jpeg, "image/jpeg")},
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/webp"
        assert "X-Conversion-Meta" in resp.headers

        meta = json.loads(resp.headers["X-Conversion-Meta"])
        assert meta["original_format"] == "JPEG"
        assert meta["width"] == 80

    def test_reject_non_image(self):
        resp = client.post(
            "/api/v1/convert/image-to-webp",
            files={"file": ("readme.txt", b"hello", "text/plain")},
        )
        assert resp.status_code == 400
