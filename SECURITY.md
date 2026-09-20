# Security

This is experimental local software. Bind to loopback by default and do not expose it to the internet. Use unique test credentials and never reuse an Epic, Steam, console, or production password. Database files and environment files may contain sensitive local data and must not be committed.

Passwords must be stored only through a modern password hash; session tokens should be random, expire, be revocable, and be stored as digests. Authentication errors should avoid account enumeration. Validate request sizes and ownership at every protected operation. Production deployment would additionally require TLS, secret management, rate limiting, audit logging, backups, dependency scanning, and a database designed for concurrency.

Analysis is read-only and limited to files the operator is authorized to inspect. This project does not support DLL injection, Epic impersonation, token or credential interception, DRM circumvention, or Easy Anti-Cheat bypass. Do not add proprietary assets, secrets, captured credentials, or copyrighted protocol dumps. Report vulnerabilities privately to the repository owner and avoid including live secrets in a report.
