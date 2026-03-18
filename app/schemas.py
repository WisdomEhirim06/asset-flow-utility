"""Pydantic response models for the API."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response returned by the health-check endpoint."""

    status: str
    version: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"status": "healthy", "version": "1.0.0"}]
        }
    }


class ConversionResponse(BaseModel):
    """Generic metadata returned after a successful conversion."""

    message: str
    original_filename: str
    record_count: int | None = Field(
        default=None,
        description="Number of records processed (CSV/JSON conversions)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Conversion completed successfully",
                    "original_filename": "data.csv",
                    "record_count": 42,
                }
            ]
        }
    }


class ImageConversionMeta(BaseModel):
    """Metadata returned alongside WebP image conversions."""

    original_filename: str
    original_format: str
    original_size_kb: float
    converted_size_kb: float
    savings_percent: float
    width: int
    height: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "original_filename": "photo.jpg",
                    "original_format": "JPEG",
                    "original_size_kb": 1024.0,
                    "converted_size_kb": 310.5,
                    "savings_percent": 69.7,
                    "width": 1920,
                    "height": 1080,
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    detail: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"detail": "Unsupported file type. Expected a CSV file."}
            ]
        }
    }
