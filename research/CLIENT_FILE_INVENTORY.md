# CLIENT FILE INVENTORY

## Executive Summary
Dauntless is built on **Unreal Engine 5** (confirmed by directory structure).
Project internal name: **Archon** (confirmed in EasyAntiCheat Settings.json)
Latest build: **2024-12-18** (very recent)

## Root Directory Files

### Executables
| Filename | Type | Size | Purpose | Confidence |
|----------|------|------|---------|-----------|
| Dauntless.exe | EXE | Main executable | Game launcher/entry point | LIKELY |
| start_protected_game.exe | EXE | Unknown | Anti-cheat/DRM launcher | LIKELY |
| Archon/Binaries/Win64/Dauntless-Win64-Shipping.exe | EXE | Main game executable | Shipped game binary | CONFIRMED |

### Manifests
| Filename | Type | Purpose | Notes |
|----------|------|---------|-------|
| Manifest_DebugFiles_Win64.txt | TXT | Debug symbol files (PDB) | Contains build symbols for Dauntless-Win64-Shipping.pdb |
| Manifest_NonUFSFiles_Win64.txt | TXT | Non-UFS game files | Game content and binaries |
| Manifest_UFSFiles_Win64.txt | TXT | UFS (Unreal File System) | Likely asset references |

### Directories
| Directory | Purpose | Confidence |
|-----------|---------|-----------|
| .egstore/ | Epic Games Store metadata | CONFIRMED |
| Archon/ | Main game project (Binaries + Content) | CONFIRMED |
| Engine/ | Unreal Engine runtime and libraries | CONFIRMED |
| EasyAntiCheat/ | Anti-cheat system integration | CONFIRMED |

## Engine Binaries (Engine/Binaries/Win64/)

### Core Runtime
| Filename | Type | Purpose | Notes |
|----------|------|---------|-------|
| CrashReportClient.exe | EXE | Crash reporter | Unreal Engine standard |
| EpicWebHelper.exe | EXE | Web connectivity helper | HTTP/networking utility |

### Key Libraries
| Filename | Type | Purpose | Evidence |
|----------|------|---------|----------|
| EOSSDK-Win64-Shipping.dll | DLL | Epic Online Services SDK | Authentication, matchmaking, lobbies, presence |
| tbb.dll | DLL | Threading Building Blocks | Multi-threading support (Intel) |
| dbgcore.dll, dbgeng.dll, dbghelp.dll | DLL | Windows debugging libraries | Crash/debug support |

**Finding:** EOSSDK is present → Dauntless uses Epic Online Services for:
- Player authentication
- Account management
- Friends/presence
- Party system
- Matchmaking
- Lobbies

## Archon Game Binaries (Archon/Binaries/Win64/)

### Main Game Executable
| Filename | Type | Compiled | Debug Info | Size Notes |
|----------|------|----------|-----------|-----------|
| Dauntless-Win64-Shipping.exe | EXE | 2024-12-18 01:36:47 UTC | PDB available | Latest build |

### C++ Libraries (Boost)
| Filename | Version | Purpose | Confidence |
|----------|---------|---------|-----------|
| boost_system-vc142-mt-x64-1_70.dll | 1.70 | C++ Standard library extensions | Networking, threading, file I/O |
| boost_thread-vc142-mt-x64-1_70.dll | 1.70 | Thread management | Multi-threaded game engine |
| boost_program_options-vc142-mt-x64-1_70.dll | 1.70 | Command-line argument parsing | Server/launcher configuration |
| boost_iostreams-vc142-mt-x64-1_70.dll | 1.70 | I/O stream operations | Network packet handling |
| boost_python39-vc142-mt-x64-1_70.dll | 1.70 | Python 3.9 bridge | Lua/Python scripting support |
| boost_regex-vc142-mt-x64-1_70.dll | 1.70 | Regular expressions | String/data parsing |
| boost_chrono-vc142-mt-x64-1_70.dll | 1.70 | Time/clock operations | Game loop timing |
| boost_atomic-vc142-mt-x64-1_70.dll | 1.70 | Atomic operations | Thread synchronization |

### Graphics Libraries
| Filename | Purpose | Notes |
|----------|---------|-------|
| OpenImageDenoise.dll | Ray-traced image denoising | Intel library for graphics |
| D3D12/D3D12Core.dll | DirectX 12 core | GPU rendering |
| tbb.dll, tbb12.dll | Threading Building Blocks | Parallel processing |

### Debug Symbols
| Filename | Type | Availability | Significance |
|----------|------|--------------|-------------|
| Dauntless-Win64-Shipping.pdb | PDB | Available | Full debug symbols for reverse engineering |

## Anti-Cheat Integration (EasyAntiCheat/)

### Configuration
- **Integration:** EasyAntiCheat_EOS_Setup.exe
- **Product ID:** prod-jackal
- **Sandbox ID:** jackal
- **Epic Games App ID:** 331370 (confirmed Dauntless on Epic Store)

### Anti-Cheat Components
| Component | Type | Purpose |
|-----------|------|---------|
| EasyAntiCheat_EOS_Setup.exe | EXE | Anti-cheat installer/configurator |
| Settings.json | JSON | Anti-cheat configuration |
| Localization files | CFG | 18 language localizations |

**Note:** Anti-cheat is integrated with EOS (Epic Online Services). A private server would need to:
1. Bypass/mock the anti-cheat system
2. Not require actual EAC authentication
3. Potentially modify the client launcher

## Game Content (Archon/Content/)

### Asset Packages
| Directory | Type | Purpose | Size Notes |
|-----------|------|---------|-----------|
| Paks/ | PAK files | Unreal Engine asset containers | Multiple numbered pak files (0-19+) |
| Movies/ | Movie files | Cinematic/intro content | Platform-specific (Windows/) |
| ThirdParty/ | Third-party assets | External integrations (ChromaEffects) | Razer peripheral support |

### PAK Structure
- Files named `Archon_X-WindowsClient.pak`
- Each pak has corresponding `.ucas` and `.utoc` files
- **ucas** = Unreal Cooked Asset Storage (asset data)
- **utoc** = Unreal Table Of Contents (index/metadata)
- **pak** = Legacy package format or descriptor

**Observation:** ~20 pak files suggest significant game content.

## Technology Stack Summary

| Category | Technology | Confidence |
|----------|-----------|-----------|
| **Game Engine** | Unreal Engine 5 | CONFIRMED |
| **Platform** | Windows (x64) | CONFIRMED |
| **Compiler** | MSVC 142 (Visual Studio 2019) | CONFIRMED |
| **Authentication** | Epic Online Services (EOS) | CONFIRMED |
| **Anti-Cheat** | EasyAntiCheat + EOS integration | CONFIRMED |
| **Online Services** | EOS (matchmaking, lobbies, presence) | LIKELY |
| **Networking** | Unreal Replication Graph (standard UE5) | LIKELY |
| **Scripting** | Python 3.9 support via Boost | POSSIBLE |
| **Graphics** | DirectX 12 + Intel denoising | CONFIRMED |

## Key Findings

1. **Unreal Engine 5** - Standard UE5 networking architecture applies
2. **Epic Online Services** - All online functionality goes through EOS
3. **Recently Compiled** - Build from 2024-12-18 suggests active development
4. **Debug Symbols Available** - PDB files enable symbol-based analysis
5. **Multi-language Support** - 18 language packs in anti-cheat
6. **DirectX 12** - Modern graphics pipeline
7. **Boost for Networking** - Custom networking layer on top of UE5

## Unknown/To-Investigate

1. Server endpoints and URLs
2. Authentication token format
3. Game session management
4. Party system implementation
5. Matchmaking algorithm and endpoints
6. Hunt/instance creation mechanics
7. Player state synchronization protocol
8. Combat system details
9. Inventory persistence format
10. Database schema (if exposed in config)

---

**Research Status:** ✓ Complete
**Next Phase:** CLIENT_ARCHITECTURE.md (Engine and game system analysis)
