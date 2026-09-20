# Safe Dauntless connection-metadata collection

This machine currently has Windows `pktmon` and `netsh`, but not Wireshark or
`tshark`. No existing HAR, pcap, pcapng, ETL, or tshark export was found in the
repository on 2026-09-20.

The safest first observation is socket and DNS-cache metadata. It can identify destination
names and addresses, TCP ports, connection timing, and local UDP bindings without
recording packet payloads, passwords, cookies, bearer tokens, or TLS secrets.

From a PowerShell prompt in the repository, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\capture_connection_metadata.ps1
```

Then launch Dauntless normally using an account and installation you are
authorized to inspect. Exercise one action at a time, noting the wall-clock
time: sign in, enter the city, start matchmaking, accept a match, travel, and
leave. Press Ctrl+C when finished. The script also stops after the game exits.

Connection and DNS CSV files are written beneath `research/local-captures/`, which is excluded from
Git. Review them locally before sharing. IP addresses can still be sensitive and
may identify service providers or a player's approximate region.

## Recovering HTTP operation shapes

Socket metadata cannot reveal HTTPS paths, methods, headers, or bodies. If an
authorized diagnostic tool produces a HAR or tshark HTTP export without
disabling TLS protections, keep the source outside Git and feed it to the
offline sanitizer:

```powershell
.\.venv\Scripts\python.exe .\analyze_capture.py C:\path\session.har `
  --output .\research\local-captures\call-map.json
```

The sanitizer retains methods, redacted URLs, status codes, header names,
parameter names, and body schemas while dropping values. Manually inspect the
result before moving any findings into a tracked research document.

Do not install interception certificates, defeat certificate pinning, decrypt
TLS, inject code, disable anti-cheat, forge Epic credentials, or upload raw
captures. `pktmon` packet capture is deliberately not used here because even a
truncated packet may retain application payload or credential material.
