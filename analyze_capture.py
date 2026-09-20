"""Build a redacted HTTP call map from an authorized HAR or tshark export.

This is deliberately an offline importer.  It never captures traffic and never
prints header values, cookies, query values, or body values.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, urlsplit, urlunsplit

MAX_INPUT_BYTES = 100 * 1024 * 1024
SENSITIVE_NAMES = {
    "authorization", "cookie", "set-cookie", "x-api-key", "api-key",
    "proxy-authorization", "x-auth-token", "session", "token",
}


def safe_url(value: str) -> tuple[str, list[str]]:
    """Return a URL with query values removed plus its query parameter names."""
    try:
        parts = urlsplit(value)
    except ValueError:
        return "[invalid-url]", []
    names = sorted({name for name, _ in parse_qs(parts.query, keep_blank_values=True).items()})
    query = "&".join(f"{name}=[redacted]" for name in names)
    # User info can contain credentials and must never be retained.
    host = parts.hostname or ""
    try:
        port = parts.port
    except ValueError:
        return "[invalid-url]", names
    if port:
        host = f"{host}:{port}"
    return urlunsplit((parts.scheme, host, parts.path, query, "")), names


def body_schema(value: Any) -> Any:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        schemas = {json.dumps(body_schema(item), sort_keys=True) for item in value}
        return {"type": "array", "items": [json.loads(item) for item in sorted(schemas)]}
    if isinstance(value, dict):
        return {"type": "object", "properties": {str(k): body_schema(v) for k, v in sorted(value.items())}}
    return "unknown"


def parse_body(text: str, mime: str) -> Any | None:
    if not text:
        return None
    try:
        if "json" in mime.lower() or text.lstrip().startswith(("{", "[")):
            return body_schema(json.loads(text))
        if "x-www-form-urlencoded" in mime.lower():
            return {"type": "object", "properties": {k: "string" for k in sorted(parse_qs(text, keep_blank_values=True))}}
    except (json.JSONDecodeError, ValueError):
        pass
    return {"type": "opaque", "content_type": mime or "unknown"}


def header_names(headers: Any) -> list[str]:
    names: set[str] = set()
    if isinstance(headers, list):
        names.update(str(h.get("name", "")).lower() for h in headers if isinstance(h, dict))
    elif isinstance(headers, dict):
        names.update(str(k).lower() for k in headers)
    return sorted(name for name in names if name)


def har_records(data: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for entry in data.get("log", {}).get("entries", []):
        request, response = entry.get("request", {}), entry.get("response", {})
        url, query_names = safe_url(str(request.get("url", "")))
        post = request.get("postData", {})
        yield {
            "method": str(request.get("method", "UNKNOWN")).upper(),
            "url": url,
            "status": response.get("status"),
            "request_header_names": header_names(request.get("headers", [])),
            "response_header_names": header_names(response.get("headers", [])),
            "query_parameter_names": query_names,
            "request_body_schema": parse_body(str(post.get("text", "")), str(post.get("mimeType", ""))),
        }


def first(layers: dict[str, Any], *names: str) -> str:
    for name in names:
        value = layers.get(name)
        if isinstance(value, list):
            value = value[0] if value else ""
        if value not in (None, ""):
            return str(value)
    return ""


def tshark_json_records(data: list[Any]) -> Iterable[dict[str, Any]]:
    for packet in data:
        layers = packet.get("_source", {}).get("layers", {}) if isinstance(packet, dict) else {}
        http = layers.get("http", layers)
        if not isinstance(http, dict):
            continue
        method = first(http, "http.request.method", "request.method")
        if not method:
            continue
        full = first(http, "http.request.full_uri", "request.full_uri")
        if not full:
            host = first(http, "http.host", "host")
            uri = first(http, "http.request.uri", "request.uri") or "/"
            full = f"http://{host}{uri}"
        url, query_names = safe_url(full)
        yield {
            "method": method.upper(), "url": url,
            "status": first(http, "http.response.code", "response.code") or None,
            "request_header_names": [], "response_header_names": [],
            "query_parameter_names": query_names, "request_body_schema": None,
        }


def csv_records(text: str) -> Iterable[dict[str, Any]]:
    for row in csv.DictReader(io.StringIO(text)):
        method = row.get("http.request.method") or row.get("method") or ""
        if not method:
            continue
        full = row.get("http.request.full_uri") or row.get("url") or ""
        if not full:
            full = f"http://{row.get('http.host', row.get('host', ''))}{row.get('http.request.uri', row.get('uri', '/'))}"
        url, query_names = safe_url(full)
        yield {"method": method.upper(), "url": url,
               "status": row.get("http.response.code") or row.get("status") or None,
               "request_header_names": [], "response_header_names": [],
               "query_parameter_names": query_names, "request_body_schema": None}


def aggregate(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        key = (record["method"], record["url"])
        item = grouped.setdefault(key, {"method": key[0], "url": key[1], "count": 0,
            "statuses": set(), "request_header_names": set(), "response_header_names": set(),
            "query_parameter_names": set(), "request_body_schemas": {}})
        item["count"] += 1
        if record.get("status") not in (None, ""):
            item["statuses"].add(str(record["status"]))
        for field in ("request_header_names", "response_header_names", "query_parameter_names"):
            item[field].update(record.get(field, []))
        schema = record.get("request_body_schema")
        if schema is not None:
            item["request_body_schemas"][json.dumps(schema, sort_keys=True)] = schema
    output = []
    for item in grouped.values():
        for field in ("statuses", "request_header_names", "response_header_names", "query_parameter_names"):
            item[field] = sorted(item[field])
        item["sensitive_header_names_present"] = sorted(
            set(item["request_header_names"] + item["response_header_names"]) & SENSITIVE_NAMES)
        item["request_body_schemas"] = list(item["request_body_schemas"].values())
        output.append(item)
    return {"format_version": 1, "redaction": "values omitted; names and schemas only", "calls": sorted(output, key=lambda x: (x["url"], x["method"]))}


def analyze(path: Path, fmt: str = "auto") -> dict[str, Any]:
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    text = path.read_text(encoding="utf-8-sig")
    chosen = fmt
    if chosen == "auto":
        chosen = "csv" if path.suffix.lower() == ".csv" else "json"
    if chosen == "csv":
        return aggregate(csv_records(text))
    data = json.loads(text)
    if isinstance(data, dict) and isinstance(data.get("log"), dict):
        return aggregate(har_records(data))
    if isinstance(data, list):
        return aggregate(tshark_json_records(data))
    raise ValueError("JSON is neither HAR nor a tshark packet array")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="authorized HAR, tshark JSON, or tshark CSV export")
    parser.add_argument("--format", choices=("auto", "json", "csv"), default="auto")
    parser.add_argument("--output", type=Path, help="write redacted JSON here (stdout by default)")
    args = parser.parse_args()
    try:
        if args.output and args.output.resolve() == args.capture.resolve():
            raise ValueError("output must not overwrite the source capture")
        result = json.dumps(analyze(args.capture, args.format), indent=2)
        if args.output:
            args.output.write_text(result + "\n", encoding="utf-8")
        else:
            print(result)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
