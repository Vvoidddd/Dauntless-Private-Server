# Known Limitations

- No verified retail Dauntless client compatibility.
- No Unreal Engine replication/game-server protocol implementation.
- No implemented Epic/EOS or PlayFab service compatibility; references in research notes are partly inferred from strings.
- No DLL injection, Epic impersonation, EAC bypass, or launcher patching.
- Official EOS developer integration is only a gated future option requiring owned credentials, terms review, and explicit design work.
- Local SQLite and an in-process API are not production multiplayer infrastructure.
- Simulated gameplay, if exposed, is a small HTTP domain model rather than real-time combat or world simulation.
- Scanner output contains false positives and proves only that printable bytes exist in a file.
- Scanner output is bounded, but a pathological uninterrupted printable sequence may still use substantial memory.
- Security hardening, load testing, deployment automation, backups, telemetry, and operational monitoring are incomplete.
- Research documents may contain outdated or overconfident inferences; running code, tests, and OpenAPI take precedence.
