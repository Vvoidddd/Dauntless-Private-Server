# CHANGELOG

## [Unreleased] - 2026-09-20 (protocol-research pivot)

### Added

- Evidence-backed static inventories for Phoenix service operations and the Unreal game-server connection stack, including executable offsets and build hash.
- Offline HAR/tshark call-map analysis that removes header, cookie, query, and body values while retaining methods, endpoints, statuses, field names, and JSON schemas.
- Capture-analysis documentation, tests, size bounds, malformed-URL handling, and source-overwrite protection.
- Metadata-only runtime observer plus a redacted failed-login timeline; the observer now records DNS-cache mappings alongside socket state.
- Exact embedded Phoenix travel template, matchmaking result fields/states, and beacon admission clues.

### Corrected

- Marked early invented endpoint lists, fixed-port assumptions, “UDP SYN,” TCP-fallback, and “95% PlayFab” claims as unverified hypotheses.
- Reframed the target architecture as Phoenix matchmaking followed by Unreal beacon reservation/reconnect, travel, and authoritative replication/RPC.

### Verified

- Full automated suite: **43 tests passed**.

## [Unreleased] - 2026-09-20

### Added

- Optional, disabled-by-default PlayFab identity linking for an operator-owned title using stable opaque Custom IDs and server-only credentials.
- Authenticated PlayFab status/link endpoints, safe upstream error handling, identity-mismatch protection, and mocked contract tests.
- Source-backed PlayFab identity, Economy V2, progression, multiplayer, configuration, and deployment research under `docs/`.
- `.gitignore` and `.env.example`; local game assets, archives, databases, secrets, environments, editor state, bytecode, and test caches are excluded from Git.

### Changed

- Removed previously tracked runtime database and Python bytecode artifacts from version control while retaining local copies.
- Documented that PlayFab supports owner-controlled infrastructure but does not provide retail Dauntless client compatibility.

### Verified

- Full automated suite: **40 tests passed**.

## [Unreleased] - 8/30/26 (2026-08-30)

### Added

- Local FastAPI foundation with application composition, health/readiness handling, account/session support, SQLite persistence, and limited simulated-gameplay modules.
- `README.md`, `ARCHITECTURE.md`, `TESTING.md`, `SECURITY.md`, and `KNOWN_LIMITATIONS.md` with explicit clean-room and non-compatibility boundaries.

### Changed

- Converted `extract_strings.py`, `extract_endpoints.py`, `find_endpoints.py`, and `find_config.py` from hardcoded one-off scripts into portable, read-only CLIs.
- Added streamed binary reads, configurable bounds, path/error validation, main guards, and argparse help to the analysis tools.

### Verified

- All four scanner scripts compile with Python and expose working `--help` output.

### Gated / not completed

- Added system, configuration, authentication, simulated-gameplay, and scanner-tooling tests plus `requirements-dev.txt`.
- Retail-client, Unreal protocol, EOS, and PlayFab compatibility were not implemented or verified.
- Any future official EOS integration requires owned credentials and terms review. DLL injection, Epic impersonation, credential interception, and EAC bypass remain out of scope.

### Integration audit

- Verified compilation of application, gameplay, test, and scanner modules.
- Ran all four scanner CLIs with bounded options against a small authorized local-client configuration file.
- Verified OpenAPI generation, the expected route inventory, fresh SQLite schema initialization, and database readiness.
- Verified tooling behavior with direct assertions and verified the full suite after installing `requirements-dev.txt`: **33 passed in 3.85 seconds**.

All notable changes to the Dauntless Private Server project are documented here.

## [RESEARCH PHASE] - 2026-08-16

### Added
- Initial project structure created
- Research directory established
- CLIENT_FILE_INVENTORY.md
  - Complete file listing
  - Technology identification
  - Dependency documentation
- CLIENT_ARCHITECTURE.md
  - Engine analysis (Unreal Engine 5 confirmed)
  - Online services model (Epic Online Services)
  - Graphics stack (DirectX 12)
  - Networking architecture
  - Launcher analysis
- NETWORKING_RESEARCH.md
  - EOS service documentation
  - Game server protocol analysis
  - Connection flow diagrams
  - Port analysis
  - Network security model
  - Inferred connection sequences
- EXPECTED_SERVER_ARCHITECTURE.md
  - Full subsystem breakdown
  - Database schema recommendations
  - API endpoint specifications
  - Interaction flow diagrams
  - Technology stack recommendations
- TODO.md - Development roadmap (16 stages)
- DONE.md - Milestone tracking
- CHANGELOG.md - Project history

### Key Discoveries
1. **Engine Identified:** Unreal Engine 5 (confirmed from directory structure and binaries)
2. **Online Platform:** Epic Online Services (EOSSDK-Win64-Shipping.dll)
3. **Networking:** Unreal Replication Graph + Boost C++ libraries
4. **Graphics:** DirectX 12 with Intel OpenImageDenoise
5. **Anti-Cheat:** EasyAntiCheat integrated with EOS
6. **Internal Name:** "Archon" (found in EasyAntiCheat config)
7. **Build Date:** 2024-12-18 (very recent)
8. **Debug Symbols:** PDB files available for analysis

### Status
- **Phase:** PHASE 0 (Client Research) - 70% Complete
- **Confidence:** HIGH (based on evidence)
- **Next:** Configuration analysis and network traffic capture

---

## Project Notes

### Research Methodology
- Non-destructive analysis only
- Read-only access to reference client
- Evidence-based conclusions only
- Confidence levels assigned to all findings
- Unknowns explicitly documented

### Compliance Checklist
- ✓ Reference client treated as READ-ONLY
- ✓ No modifications to original files
- ✓ No proprietary content in server tree (not yet created)
- ✓ No secrets/credentials documented
- ✓ No circumvention of security systems attempted
- ✓ Purpose: Interoperability research

---

## Version History

### v0.1.0 - Research Initialization
- Date: 2026-08-16
- Phase: PHASE 0 (Client Analysis)
- Scope: Technology identification and architecture reconstruction
- Status: Research phase initiated
- Completeness: 70% of Phase 0

---

## Roadmap (Planned)

### v0.2.0 - Configuration Discovery
- Extract server endpoints from client
- Analyze network traffic
- Document actual protocol details
- Update CONFIGURATION.md

### v0.3.0 - Gameplay Systems
- Deep analysis of game mechanics
- Document hunt system
- Document combat calculations
- Document progression system
- Complete GAMEPLAY_RESEARCH.md

### v0.4.0 - Server Skeleton
- Initialize server codebase
- Set up development environment
- Create project structure
- Implement logging

### v0.5.0 - Database Layer
- Design schema
- Implement database models
- Create migrations
- Write utility functions

### v1.0.0 - Alpha Implementation
- Authentication service
- Player accounts
- Lobby world
- Hunt instances
- Combat system
- Persistence

### v2.0.0 - Multi-Player Testing
- Multiplayer synchronization
- Performance tuning
- Stability improvements
- Load testing

### v3.0.0 - Feature Complete
- All game systems
- Full progression
- Inventory management
- Cosmetics/appearance
- Social features

---

## Known Limitations

### Phase 0 Limitations
1. No network traffic capture performed yet
2. Asset pak contents not analyzed
3. Exact server endpoints unknown
4. Protocol details inferred, not confirmed
5. Database schema reconstructed from client expectations

### Server Implementation Limitations (TBD)
- Single-region deployment (initial)
- No cloud backup (initial)
- Limited scaling (initial)
- Anti-cheat bypass required (likely)
- EOS mock/replacement required

---

## Breaking Changes
None yet (research phase).

---

## Notes for Future Developers

1. **Do not skip the research phase** - Client analysis informs every server design decision
2. **Document assumptions** - The EXPECTED_SERVER_ARCHITECTURE is a model, not confirmed design
3. **Implement stages incrementally** - Complete one stage before moving to the next
4. **Test thoroughly** - Each stage must be validated before building on it
5. **Update documentation** - Keep DONE.md and TODO.md in sync

---

## Contributors
- Initial research: AI Assistant (GitHub Copilot)
- Project initiator: User
- Reference materials: Dauntless client (legally obtained)

---

Last Updated: 2026-08-16
