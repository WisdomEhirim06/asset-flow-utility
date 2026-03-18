"""Image → WebP conversion logic using Pillow."""

from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image

from app.exceptions import ConversionError, InvalidFileError

ALLOWED_FORMATS = {"JPEG", "PNG"}


@dataclass(frozen=True)
class WebPResult:
    """Container for the conversion output and its metadata."""

    image_bytes: bytes
    original_format: str
    original_size_kb: float
    converted_size_kb: float
    savings_percent: float
    width: int
    height: int


def convert_to_webp(file_bytes: bytes, filename: str, quality: int = 80) -> WebPResult:
    """Convert a JPEG or PNG image to WebP format.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the uploaded image.
    filename:
        Original filename (used for error messages).
    quality:
        WebP quality setting (1–100).

    Returns
    -------
    WebPResult
        The converted image bytes together with useful metadata.
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception:
        raise InvalidFileError(
            f"'{filename}' could not be opened as an image. "
            "Please upload a valid JPEG or PNG file."
        )

    fmt = image.format
    if fmt not in ALLOWED_FORMATS:
        raise InvalidFileError(
            f"Unsupported image format: '{fmt}'. "
            f"Allowed formats: {', '.join(sorted(ALLOWED_FORMATS))}."
        )

    try:
        buffer = io.BytesIO()
        # Ensure RGB mode (handles RGBA PNGs, palette images, etc.)
        rgb_image = image.convert("RGB") if image.mode != "RGB" else image
        rgb_image.save(buffer, format="WEBP", quality=quality)
        webp_bytes = buffer.getvalue()
    except Exception as exc:
        raise ConversionError(f"WebP conversion failed: {exc}")

    original_kb = len(file_bytes) / 1024
    converted_kb = len(webp_bytes) / 1024
    savings = ((original_kb - converted_kb) / original_kb) * 100 if original_kb > 0 else 0.0

    return WebPResult(
        image_bytes=webp_bytes,
        original_format=fmt,
        original_size_kb=round(original_kb, 2),
        converted_size_kb=round(converted_kb, 2),
        savings_percent=round(savings, 1),
        width=image.width,
        height=image.height,
    )
