"""Unit tests for the image → WebP conversion service."""

import io
import pytest
from PIL import Image

from app.exceptions import InvalidFileError
from app.services.image import convert_to_webp


def _make_image(fmt: str = "JPEG", size: tuple[int, int] = (100, 100)) -> bytes:
    """Create a minimal in-memory image and return its bytes."""
    img = Image.new("RGB", size, color="red")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


class TestConvertToWebp:
    def test_jpeg_to_webp(self):
        jpeg_bytes = _make_image("JPEG")
        result = convert_to_webp(jpeg_bytes, "photo.jpg", quality=80)

        assert result.original_format == "JPEG"
        assert result.width == 100
        assert result.height == 100
        assert result.converted_size_kb > 0
        # Verify the output is valid WebP
        img = Image.open(io.BytesIO(result.image_bytes))
        assert img.format == "WEBP"

    def test_png_to_webp(self):
        png_bytes = _make_image("PNG")
        result = convert_to_webp(png_bytes, "icon.png", quality=80)

        assert result.original_format == "PNG"
        assert result.width == 100
        assert result.height == 100

    def test_rgba_png_to_webp(self):
        """RGBA images should be converted to RGB before saving as WebP."""
        img = Image.new("RGBA", (50, 50), color=(255, 0, 0, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        result = convert_to_webp(png_bytes, "transparent.png")
        assert result.original_format == "PNG"

    def test_invalid_image_raises(self):
        with pytest.raises(InvalidFileError, match="could not be opened"):
            convert_to_webp(b"not-an-image", "broken.jpg")

    def test_unsupported_format_raises(self):
        # BMP is not in ALLOWED_FORMATS
        img = Image.new("RGB", (10, 10), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="BMP")
        bmp_bytes = buf.getvalue()

        with pytest.raises(InvalidFileError, match="Unsupported image format"):
            convert_to_webp(bmp_bytes, "image.bmp")

    def test_metadata_savings(self):
        jpeg_bytes = _make_image("JPEG", (200, 200))
        result = convert_to_webp(jpeg_bytes, "big.jpg", quality=50)

        assert result.original_size_kb > 0
        assert result.converted_size_kb > 0
        assert isinstance(result.savings_percent, float)
