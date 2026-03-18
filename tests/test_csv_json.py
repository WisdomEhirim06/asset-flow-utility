"""Unit tests for the CSV ↔ JSON conversion service."""

import json

import pytest

from app.exceptions import ConversionError, InvalidFileError
from app.services.csv_json import csv_to_json, json_to_csv


# ---------------------------------------------------------------------------
# csv_to_json
# ---------------------------------------------------------------------------

class TestCsvToJson:
    def test_basic_conversion(self):
        csv_data = b"name,age,city\nAlice,30,NYC\nBob,25,LA\n"
        records, count = csv_to_json(csv_data, "test.csv")

        assert count == 2
        assert records[0]["name"] == "Alice"
        assert records[1]["city"] == "LA"

    def test_single_row(self):
        csv_data = b"id,value\n1,hello\n"
        records, count = csv_to_json(csv_data, "test.csv")

        assert count == 1
        assert records[0] == {"id": "1", "value": "hello"}

    def test_empty_csv_headers_only(self):
        csv_data = b"name,age\n"
        records, count = csv_to_json(csv_data, "test.csv")

        assert count == 0
        assert records == []

    def test_invalid_encoding_raises(self):
        bad_bytes = b"\xff\xfe\x00\x01"
        with pytest.raises(InvalidFileError, match="could not be decoded"):
            csv_to_json(bad_bytes, "bad.csv")


# ---------------------------------------------------------------------------
# json_to_csv
# ---------------------------------------------------------------------------

class TestJsonToCsv:
    def test_basic_conversion(self):
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        csv_text, count = json_to_csv(json.dumps(data).encode(), "test.json")

        assert count == 2
        assert "name,age" in csv_text
        assert "Alice,30" in csv_text

    def test_invalid_json_raises(self):
        with pytest.raises(InvalidFileError, match="not valid JSON"):
            json_to_csv(b"not json at all", "bad.json")

    def test_single_object_wraps_to_array(self):
        csv_text, count = json_to_csv(b'{"name": "Alice", "age": 30}', "obj.json")
        assert count == 1
        assert "Alice" in csv_text

    def test_empty_array_raises(self):
        with pytest.raises(ConversionError, match="empty"):
            json_to_csv(b"[]", "empty.json")

    def test_array_of_non_objects_raises(self):
        with pytest.raises(InvalidFileError, match="array of objects"):
            json_to_csv(b'[1, 2, 3]', "nums.json")

    def test_nested_objects_are_flattened(self):
        data = [{"name": "Alice", "address": {"city": "NYC", "zip": "10001"}}]
        csv_text, count = json_to_csv(json.dumps(data).encode(), "nested.json")

        assert count == 1
        assert "address.city" in csv_text
        assert "address.zip" in csv_text
        assert "NYC" in csv_text
