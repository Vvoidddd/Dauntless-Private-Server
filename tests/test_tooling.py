"""Focused tests for the read-only top-level analysis utilities."""

from pathlib import Path

from extract_endpoints import classify
from extract_strings import printable_strings


def test_printable_strings_cross_chunk_boundary(tmp_path: Path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"\x00https://example.com\x00tail\x00")
    assert list(printable_strings(sample, minimum=4, chunk_size=5)) == [
        "https://example.com",
        "tail",
    ]


def test_endpoint_classification_rejects_invalid_ip_and_port():
    assert classify("https://example.com/path") == "URLs"
    assert classify("api.example.com:443") == "Host names"
    assert classify("127.0.0.1:7777") == "IP addresses"
    assert classify("999.0.0.1:7777") is None
    assert classify("127.0.0.1:99999") is None


def test_printable_strings_is_read_only(tmp_path: Path):
    sample = tmp_path / "sample.bin"
    original = b"\x00playfab.example\x00"
    sample.write_bytes(original)
    list(printable_strings(sample, minimum=4, chunk_size=4))
    assert sample.read_bytes() == original
