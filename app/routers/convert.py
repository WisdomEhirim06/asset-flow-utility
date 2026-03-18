"""File-conversion endpoints: CSV ↔ JSON and Image → WebP."""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, Response

from app.config import settings
from app.exceptions import FileTooLargeError, InvalidFileError
from app.schemas import ConversionResponse, ErrorResponse, ImageConversionMeta
from app.services.csv_json import csv_to_json, json_to_csv
from app.services.image import convert_to_webp

router = APIRouter(prefix="/api/v1/convert", tags=["Conversion"])

_MB = 1024 * 1024


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _read_upload(file: UploadFile, allowed_extensions: set[str]) -> bytes:
    """Read uploaded file bytes with size & extension validation."""
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in allowed_extensions:
        raise InvalidFileError(
            f"Unsupported file extension '.{ext}'. "
            f"Allowed: {', '.join(sorted('.' + e for e in allowed_extensions))}."
        )

    contents = await file.read()

    max_bytes = settings.max_file_size_mb * _MB
    if len(contents) > max_bytes:
        raise FileTooLargeError(
            f"File size ({len(contents) / _MB:.1f} MB) exceeds the "
            f"{settings.max_file_size_mb} MB limit."
        )

    return contents


# ------------------------------------------------------------------
# CSV → JSON
# ------------------------------------------------------------------

@router.post(
    "/csv-to-json",
    response_model=ConversionResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    summary="Convert CSV to JSON",
    description=(
        "Upload a CSV file and receive a JSON array of objects. "
        "Each row becomes one object whose keys are the CSV headers."
    ),
)
async def csv_to_json_endpoint(
    file: UploadFile = File(..., description="A CSV file to convert"),
):
    contents = await _read_upload(file, {"csv"})
    records, count = csv_to_json(contents, file.filename or "upload.csv")

    return JSONResponse(
        content={
            "message": "CSV converted to JSON successfully",
            "original_filename": file.filename,
            "record_count": count,
            "data": records,
        }
    )


# ------------------------------------------------------------------
# JSON → CSV
# ------------------------------------------------------------------

@router.post(
    "/json-to-csv",
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    summary="Convert JSON to CSV",
    description=(
        "Upload a JSON file containing an array of objects and receive "
        "a downloadable CSV file."
    ),
)
async def json_to_csv_endpoint(
    file: UploadFile = File(..., description="A JSON file to convert"),
):
    contents = await _read_upload(file, {"json"})
    csv_text, _count = json_to_csv(contents, file.filename or "upload.json")

    original_name = (file.filename or "converted").rsplit(".", 1)[0]
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{original_name}.csv"'
        },
    )


# ------------------------------------------------------------------
# Image → WebP
# ------------------------------------------------------------------

@router.post(
    "/image-to-webp",
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    summary="Convert image to WebP",
    description=(
        "Upload a JPEG or PNG image and receive an optimized WebP version. "
        "Conversion metadata (sizes, savings) is returned via response headers."
    ),
)
async def image_to_webp_endpoint(
    file: UploadFile = File(..., description="A JPEG or PNG image to convert"),
):
    contents = await _read_upload(file, {"jpg", "jpeg", "png"})
    result = convert_to_webp(contents, file.filename or "image", quality=settings.webp_quality)

    meta = ImageConversionMeta(
        original_filename=file.filename or "image",
        original_format=result.original_format,
        original_size_kb=result.original_size_kb,
        converted_size_kb=result.converted_size_kb,
        savings_percent=result.savings_percent,
        width=result.width,
        height=result.height,
    )

    original_name = (file.filename or "converted").rsplit(".", 1)[0]
    return Response(
        content=result.image_bytes,
        media_type="image/webp",
        headers={
            "Content-Disposition": f'attachment; filename="{original_name}.webp"',
            "X-Conversion-Meta": meta.model_dump_json(),
        },
    )
