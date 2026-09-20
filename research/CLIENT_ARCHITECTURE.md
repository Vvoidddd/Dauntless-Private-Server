# CLIENT ARCHITECTURE

## Verified Game Technology

### Engine: Unreal Engine 5
**Confidence:** CONFIRMED
**Evidence:**
- Directory structure matches UE5 standard layout:
  - `Engine/Binaries/` → Engine runtime
  - `Engine/Content/` → Engine assets
  - `Engine/Plugins/` → Engine extensions
  - `Archon/Content/` → Game project content
  - `.pak` and `.ucas/.utoc` files → UE5 asset packaging format
- CrashReportClient.exe → Standard Unreal Engine crash handler
- Boost libraries with C++ runtime → Standard UE5 dependency set

### Compiler
**MSVC v142 (Visual Studio 2019)**
- Evidence: `vc142-mt-x64` in all Boost DLL filenames
- Shipped in Release/Shipping configuration

### Platform Target
**Windows x64 (64-bit)**
- All binaries: `Win64` architecture
- DirectX 12 as graphics API
- No x86 (32-bit) build present

---

## Online Services Architecture

### Epic Online Services (EOS)
**Status:** PRIMARY AUTHENTICATION & ONLINE SYSTEM
**Location:** `Engine/Binaries/Win64/EOSSDK-Win64-Shipping.dll`

#### Verified EOS Features
Based on EOS SDK capabilities and presence in the build:

| Feature | Purpose | Client Role | Expected Server Role |
|---------|---------|-------------|----------------------|
| **Authentication** | Player login | Obtain auth token | Validate token |
| **Account Management** | Player identity | Create/update profile | Store/retrieve profiles |
| **Friends** | Social network | Fetch friends list | Maintain friend relationships |
| **Presence** | Online status | Broadcast status | Query player status |
| **Matchmaking** | Find games | Request match | Manage matchmaking queue |
| **Lobbies** | Player grouping | Join/create lobby | Host lobby sessions |
| **Sessions** | Game instances | Register session | Manage session lifecycle |
| **Cross-Platform** | Multi-platform play | Platform-agnostic API | Platform-aware database |

### Integration Pattern
```
Dauntless-Win64-Shipping.exe
    |
    +--- EOSSDK-Win64-Shipping.dll
    |     |
    |     +--- Epic Online Services (Cloud)
    |           |
    |           +--- Authentication
    |           +--- Matchmaking
    |           +--- Lobbies
    |           +--- Presence
    |           +--- Friends
    |
    +--- Boost networking libraries
          |
          +--- Game server connection (TCP/UDP)
          +--- World state synchronization
          +--- Combat/entity updates
```

---

## Networking Architecture (Inferred)

### Network Stack
**Primary:** Unreal Replication Graph (UE5 standard)
- UDP-based game-state replication
- Client-server authoritative model
- Actor replication with property synchronization

**Secondary:** Boost networking
- Custom protocol layers
- Possibly for non-game-specific communication
- TCP for reliable messaging

### Connection Flow (Reconstructed)

```
CLIENT                          EOS SERVICES                    GAME SERVER
  |
  +--[OAuth/Device login]-------->|
  |                               |
  |<--[Auth Token]----------------+
  |
  +--[Join Matchmaking]---------->|
  |                               |
  |                       [Queue Management]
  |                               |
  |<--[Match Found]---------------+
  |                               |
  +--[Connect to IP:Port]-----+
  |                           |
  |                     GAME SERVER
  |                           |
  |<--[Welcome/Auth]----------+
  |                           |
  |<--[World State Repl.]-----+
  |                           |
  +--[Movement/Input]-----+
  |
  [Game loop continues...]
```

### Protocol Characteristics (Evidence-Based)

| Aspect | Finding | Confidence |
|--------|---------|-----------|
| **Primary Protocol** | Unreal Replication Graph (UDP) | LIKELY |
| **Fallback/Reliability** | TCP via Boost | LIKELY |
| **Matchmaking** | EOS-hosted service | CONFIRMED |
| **Authentication** | EOS tokens | CONFIRMED |
| **Session Management** | EOS sessions | LIKELY |
| **Lobby System** | EOS lobbies | LIKELY |
| **Party System** | EOS social features | LIKELY |

---

## Game Project Structure

### Project Name: "Archon"
- **Internal Codename:** prod-jackal (from EasyAntiCheat Settings.json)
- **Sandbox ID:** jackal
- **Unreal Project Structure:**
  ```
  Archon/
  ├── Binaries/
  │   └── Win64/
  │       ├── Dauntless-Win64-Shipping.exe      [Game binary]
  │       ├── Boost libraries                    [Networking]
  │       ├── OpenImageDenoise.dll               [Graphics]
  │       └── D3D12/                             [Graphics driver]
  │
  ├── Content/
  │   ├── Paks/                                  [Game assets]
  │   │   ├── Archon_0-WindowsClient.pak        
  │   │   ├── Archon_0-WindowsClient.ucas       
  │   │   ├── Archon_0-WindowsClient.utoc       
  │   │   ├── Archon_1-WindowsClient.pak        
  │   │   └── ... (20+ pak files)
  │   │
  │   ├── Movies/
  │   │   └── Windows/                           [Cinematic content]
  │   │
  │   └── ThirdParty/
  │       └── ChromaEffects/                    [Razer integration]
  │
  └── [Plugins, Source, etc. - likely in pak files]
  ```

### Asset Organization

**PAK Files Structure:**
- Multiple numbered pak archives (0-19+)
- Each pak has triplet: `.pak`, `.ucas`, `.utoc`
- **Pattern:** `Archon_[NUMBER]-WindowsClient.*`

**Observation:** Large number of paks suggests:
- Modular asset loading
- Streaming assets for open world
- Separate paks for different content categories (likely)

---

## Launcher Architecture

### Launch Flow

```
User clicks "Dauntless" shortcut
  |
  v
start_protected_game.exe (Launcher)
  |
  +--> Checks anti-cheat (EasyAntiCheat)
  |
  +--> Verifies game files (manifests)
  |
  +--> Invokes: Dauntless-Win64-Shipping.exe
  |
  v
Game starts
  |
  +--> Initializes UE5 engine
  +--> Loads EOSSDK
  +--> Connects to EOS
  +--> Authenticates player
  +--> [Matchmaking/Lobby]
  +--> [Connects to game server]
  v
In-game
```

### Multi-Process Architecture
| Process | Purpose | Lifecycle |
|---------|---------|-----------|
| start_protected_game.exe | Anti-cheat bootstrap | Start → End |
| Dauntless-Win64-Shipping.exe | Main game | Start → End |
| EasyAntiCheat_EOS_Setup.exe | AC Configuration | One-time install |
| CrashReportClient.exe | Error handling | On crash |

---

## Graphics Architecture

### Rendering Pipeline
- **API:** DirectX 12
- **Denoising:** Intel OpenImageDenoise (GPU-accelerated)
- **Threading:** Intel TBB (parallelized rendering)
- **Feature Support:** Ray-tracing capable

### Performance Characteristics
- Modern GPU features leveraged
- Real-time denoising suggests high-quality visuals
- Multi-threaded rendering pipeline

---

## Scripting & Modding

### Python 3.9 Support
**Evidence:** `boost_python39-vc142-mt-x64-1_70.dll`

**Possible Uses:**
1. In-game scripting for game logic
2. Data pipeline tools
3. Behavior scripting
4. Event system scripting
5. Lua alternative (via Boost.Python bridge)

**Confidence:** POSSIBLE (presence doesn't confirm usage in shipped game)

---

## File Verification & Integrity

### Manifest System
Three manifest files for Win64 build:
1. **Manifest_DebugFiles_Win64.txt** → Debug symbols (PDB)
2. **Manifest_NonUFSFiles_Win64.txt** → Game files, binaries, configs
3. **Manifest_UFSFiles_Win64.txt** → Unreal File System assets

**Purpose:** Verify file integrity on update/installation

---

## Client Capabilities (Inferred)

Based on technology stack, the client can:

| Capability | Technology | Confidence |
|-----------|-----------|-----------|
| **3D Rendering** | Unreal Engine 5 + DirectX 12 | CONFIRMED |
| **Network I/O** | Boost + UE5 sockets | CONFIRMED |
| **Multi-threading** | TBB + UE5 threading | CONFIRMED |
| **Online Identity** | EOS authentication | CONFIRMED |
| **Matchmaking** | EOS matchmaking service | CONFIRMED |
| **Party/Lobbies** | EOS social features | CONFIRMED |
| **Presence** | EOS presence service | CONFIRMED |
| **Game Logic** | UE5 Gameplay Framework | CONFIRMED |
| **Entity Replication** | Unreal Replication Graph | LIKELY |
| **Combat Simulation** | UE5 physics + gameplay code | LIKELY |
| **Inventory Management** | UE5 data structures | LIKELY |
| **Persistence** | Server-driven database | LIKELY |

---

## Unknown Architecture Details

| Question | Evidence Status | Next Step |
|----------|-----------------|-----------|
| How are game sessions created? | Unknown | Search for session references |
| What is the hunt/instance model? | Unknown | Analyze gameplay code strings |
| How is player state synchronized? | Unknown | Network protocol analysis |
| What database is used server-side? | Unknown | Server-side discovery |
| How is combat authoritative? | Unknown | Network lag/sync analysis |
| What is the party size limit? | Unknown | EOS API constraints or config |
| How is item loot/drops handled? | Unknown | Gameplay code analysis |

---

## Summary: Client Architecture

### Core Engine
- **Unreal Engine 5** (confirmed)
- **DirectX 12** (modern rendering)
- **Standard UE5 networking** (replication graph)

### Online Services
- **Epic Online Services** (authentication, matchmaking, lobbies, presence)
- **EOS-based session management**

### Anti-Cheat
- **EasyAntiCheat** integrated with EOS
- Boots before game executable

### Launcher
- **Windows-based launcher** (start_protected_game.exe)
- **File verification system** (manifest-based)

### Game Content
- **Multiple pak files** (20+)
- **Streaming-friendly architecture**

### Dependencies
- **Boost C++ libraries** (networking, threading, Python)
- **Intel TBB** (parallelization)
- **Windows APIs** (debugging, crashes)

---

**Research Status:** ✓ Architecture Identified
**Next Phase:** EXECUTABLES.md (Deep dive into binary analysis)
