import json

from analyze_capture import analyze, body_schema, safe_url


def test_har_redacts_all_values_and_reports_schema(tmp_path):
    secret = "SUPER_SECRET_TOKEN"
    har = {"log": {"entries": [{
        "request": {
            "method": "POST",
            "url": f"https://user:password@api.example.test/v1/login?ticket={secret}&platform=pc",
            "headers": [{"name": "Authorization", "value": secret}, {"name": "X-Trace", "value": "abc"}],
            "postData": {"mimeType": "application/json", "text": json.dumps({"email": "me@example.test", "password": secret, "nested": {"remember": True}})},
        },
        "response": {"status": 200, "headers": [{"name": "Set-Cookie", "value": secret}]},
    }]}}
    source = tmp_path / "sample.har"
    source.write_text(json.dumps(har), encoding="utf-8")
    result = analyze(source)
    serialized = json.dumps(result)
    assert secret not in serialized and "password@" not in serialized and "me@example.test" not in serialized
    call = result["calls"][0]
    assert call["url"] == "https://api.example.test/v1/login?platform=[redacted]&ticket=[redacted]"
    assert call["sensitive_header_names_present"] == ["authorization", "set-cookie"]
    assert call["request_body_schemas"][0]["properties"]["nested"]["properties"]["remember"] == "boolean"


def test_tshark_json_and_csv(tmp_path):
    packet = [{"_source": {"layers": {"http": {
        "http.request.method": "GET", "http.host": "api.example.test",
        "http.request.uri": "/status?token=do-not-output", "http.response.code": "204"
    }}}}]
    source = tmp_path / "packets.json"
    source.write_text(json.dumps(packet), encoding="utf-8")
    assert analyze(source)["calls"][0]["url"].endswith("token=[redacted]")

    csv_file = tmp_path / "packets.csv"
    csv_file.write_text("method,url,status\nPUT,https://example.test/a?id=123,201\n", encoding="utf-8")
    assert analyze(csv_file)["calls"][0]["statuses"] == ["201"]


def test_schema_and_malformed_url_are_value_free():
    assert body_schema([1, "secret", False]) == {"type": "array", "items": ["boolean", "number", "string"]}
    assert safe_url("https://name:secret@example.test/path#token")[0] == "https://example.test/path"
    assert safe_url("https://example.test:99999/path")[0] == "[invalid-url]"
