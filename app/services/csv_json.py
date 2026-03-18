"""CSV ↔ JSON conversion logic."""

from __future__ import annotations

import csv
import io
import json

from app.exceptions import ConversionError, InvalidFileError


def csv_to_json(file_bytes: bytes, filename: str) -> tuple[list[dict], int]:
    """Convert CSV bytes to a list of dictionaries.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the uploaded CSV file.
    filename:
        Original filename (used for error messages).

    Returns
    -------
    tuple
        A ``(records, count)`` pair where *records* is the parsed list of
        row-dicts and *count* is the number of rows.

    Raises
    ------
    InvalidFileError
        If the file cannot be decoded as UTF-8 text.
    ConversionError
        If parsing fails for any other reason.
    """
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise InvalidFileError(
            f"'{filename}' could not be decoded as UTF-8. "
            "Please make sure the file is a valid CSV."
        )

    try:
        reader = csv.DictReader(io.StringIO(text))
        records: list[dict] = list(reader)
        return records, len(records)
    except csv.Error as exc:
        raise ConversionError(f"Failed to parse CSV: {exc}")


def _flatten(obj: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Recursively flatten a nested dict into dot-notation keys.

    Nested dicts are expanded (``profile.contact.email``), while lists
    and other non-dict values are serialized as JSON strings.
    """
    items: list[tuple[str, object]] = []
    for key, value in obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(_flatten(value, new_key, sep).items())
        elif isinstance(value, (list, tuple)):
            items.append((new_key, json.dumps(value)))
        else:
            items.append((new_key, value))
    return dict(items)


def json_to_csv(file_bytes: bytes, filename: str) -> tuple[str, int]:
    """Convert a JSON array of objects to a CSV string.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the uploaded JSON file.
    filename:
        Original filename (used for error messages).

    Returns
    -------
    tuple
        A ``(csv_text, count)`` pair where *csv_text* is the resulting CSV
        string and *count* is the number of records.

    Raises
    ------
    InvalidFileError
        If the content is not valid JSON or not an array of objects.
    ConversionError
        If writing CSV fails.
    """
    # Decode bytes to str first — handles UTF-8 BOM and UTF-16 Windows files
    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("utf-16")
        except UnicodeDecodeError:
            raise InvalidFileError(
                f"'{filename}' could not be decoded. "
                "Please save the file as UTF-8."
            )

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidFileError(
            f"'{filename}' is not valid JSON: {exc}"
        )

    # Accept a single object — wrap it into a one-element list
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise InvalidFileError(
            "Expected a JSON array of objects or a single JSON object, e.g. "
            '[{"name": "Alice", "age": 30}, ...] or {"name": "Alice", "age": 30}'
        )

    if len(data) == 0:
        raise ConversionError("The JSON array is empty — nothing to convert.")

    try:
        # Flatten nested objects into dot-notation columns
        flat_data = [_flatten(record) for record in data]

        # Collect ALL field names across every record (order-preserving)
        fieldnames: list[str] = []
        seen: set[str] = set()
        for row in flat_data:
            for key in row:
                if key not in seen:
                    fieldnames.append(key)
                    seen.add(key)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(flat_data)
        return output.getvalue(), len(flat_data)
    except (csv.Error, KeyError) as exc:
        raise ConversionError(f"Failed to write CSV: {exc}")

