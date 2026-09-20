# Offline HTTP call-map analysis

`analyze_capture.py` converts an **already exported, authorized** HAR or tshark
JSON/CSV file into a compact call map. It reports HTTP methods, redacted URLs,
status codes, header names, query-parameter names, and JSON/form body schemas.
It never writes header values, cookie values, query values, or body values.

```powershell
python analyze_capture.py my-session.har --output call-map.json
python analyze_capture.py tshark-export.json --output call-map.json
python analyze_capture.py tshark-fields.csv --format csv --output call-map.json
```

For tshark JSON, export decoded HTTP fields as a packet array (`-T json`). For
CSV, supported columns include `http.request.method`, `http.request.full_uri`,
`http.host`, `http.request.uri`, and `http.response.code`; the shorter names
`method`, `url`, and `status` are also accepted. HAR gives the richest result
because it associates request bodies and response headers with each request.

Treat the source capture as sensitive even though the generated call map is
redacted. Store it outside Git and delete it according to your data-retention
policy. Review generated output before sharing it. Only analyze traffic and
accounts you are authorized to inspect.

This utility does not capture traffic, install certificates, intercept TLS,
defeat certificate pinning, modify a client, or bypass authentication/anti-cheat.
It is intended to turn legitimately obtained diagnostic exports into evidence
for a clean-room implementation.
