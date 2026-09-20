# EXPECTED SERVER ARCHITECTURE

## Overview

Based on client analysis, this document reconstructs what server-side systems must exist to support Dauntless gameplay.

---

## System Architecture Model

```
PRIVATE SERVER INFRASTRUCTURE
│
├─── Authentication Layer
│    ├── Account management
│    ├── Token generation/validation
│    └── Session management
│
├─── Game Services
│    ├── Lobby/Ramsgate world
│    ├── Party system
│    ├── Matchmaking
│    ├── Hunt instance manager
│    └── Game server (authoritative)
│
├─── World State
│    ├── Player positions
│    ├── Entity/behemoth positions
│    ├── Environmental state
│    └── Loot/drops
│
├─── Gameplay Systems
│    ├── Combat resolver
│    ├── Damage calculation
│    ├── Hit detection
│    ├── Status effects
│    └── Loot generation
│
├─── Persistence Layer
│    ├── Player accounts
│    ├── Character data
│    ├── Inventory
│    ├── Progression/levels
│    ├── Equipment/loadouts
│    └── Hunt history
│
└─── Data Backend
     └── Database (PostgreSQL / MySQL / SQLite)
```

---

## Subsystem Breakdown

### 1. Authentication Service

**CLIENT EXPECTATION:**
- Player provides email/password (or Discord ID)
- Receives auth token
- Token used to authenticate with game server
- Session persists across reconnects (same match)

**SERVER REQUIREMENT:**
```
Database Tables:
  - accounts (id, email, password_hash, created_at, updated_at)
  - sessions (id, account_id, token, expiry, ip_address, created_at)
  - characters (id, account_id, name, level, created_at)

API Endpoints:
  POST   /auth/register
  POST   /auth/login
  POST   /auth/logout
  POST   /auth/validate-token
  GET    /profile/{player_id}
  PUT    /profile/{player_id}

Responsibilities:
  - Hash passwords (Argon2id)
  - Issue JWT or bearer tokens
  - Track login sessions
  - Prevent account takeover
  - Track last login
```

**EVIDENCE:**
- EOSSDK present → auth service required
- start_protected_game.exe → launcher handles auth UI
- Session-based gameplay → server must track sessions

**CONFIDENCE:** CONFIRMED

---

### 2. Account & Player Profile

**CLIENT EXPECTATION:**
- Player has single account with multiple characters
- Each character has name, level, position in world
- Profile accessible from lobby

**SERVER REQUIREMENT:**
```
Database Tables:
  - accounts
  - characters (id, account_id, name, class, level, position_x, position_y, position_z, experience, created_at)
  - equipment (id, character_id, weapon_id, armor_head_id, armor_chest_id, armor_gloves_id, armor_legs_id)

API Endpoints:
  GET    /characters/{character_id}
  PUT    /characters/{character_id}
  POST   /characters (create new)
  DELETE /characters/{character_id}
  GET    /characters/{character_id}/equipment

Responsibilities:
  - Store character attributes
  - Track character progression
  - Manage equipment/builds
  - Support multiple characters per account
```

**EVIDENCE:**
- Character creation screens in UI
- Loadout selection before hunts
- Level/progression system

**CONFIDENCE:** CONFIRMED

---

### 3. Lobby / Ramsgate World

**CLIENT EXPECTATION:**
- Players spawn in shared hub (Ramsgate)
- See other players as entities
- Can interact (chat, party invites, trade)
- Persistent world lobby

**SERVER REQUIREMENT:**
```
Components:
  - World server instance (always running)
  - Player entity spawning (on login)
  - NPC entities (quest givers, vendors, etc.)
  - Chat system (local)

Database:
  - world_spawns (id, entity_type, x, y, z, name)
  - npcs (id, name, type, dialogue)
  - shops (id, npc_id, item_id, price)

Network:
  - Continuous actor replication
  - Low update rate (~2-5 Hz acceptable)
  - Player position broadcasting
  - NPC state synchronization

Responsibilities:
  - Manage persistent world
  - Spawn players on connect
  - Handle entity despawn on disconnect
  - Manage vendor/shop interactions
```

**EVIDENCE:**
- Ramsgate mentioned in requirements
- Expected 12-player lobby
- Party system implies shared space

**CONFIDENCE:** LIKELY

---

### 4. Party System

**CLIENT EXPECTATION:**
- Players can create/join parties (2-4 players?)
- Party shown in UI
- Party matchmaking (grouped hunt)
- Party chat

**SERVER REQUIREMENT:**
```
Database Tables:
  - parties (id, leader_id, name, max_size, created_at)
  - party_members (id, party_id, character_id, join_time)

API Endpoints:
  POST   /parties (create)
  GET    /parties/{party_id}
  POST   /parties/{party_id}/invite
  POST   /parties/{party_id}/join
  POST   /parties/{party_id}/leave
  DELETE /parties/{party_id} (disband)

Responsibilities:
  - Track party membership
  - Validate party invites
  - Manage party lifecycle
  - Route matchmaking requests to party leader
  - Broadcast party changes to members
```

**EVIDENCE:**
- Party system explicitly required
- Multiplayer gameplay (4-player hunts common)
- EOS social features support this

**CONFIDENCE:** CONFIRMED

---

### 5. Matchmaking Service

**CLIENT EXPECTATION:**
- Player/party initiates "find hunt"
- Waits in queue (variable time)
- Match found, players transported to hunt instance
- Game server assigned

**SERVER REQUIREMENT:**
```
Components:
  - Matchmaking queue
  - Matching algorithm
  - Server selection/allocation

Database:
  - matchmaking_queue (id, player_id/party_id, queue_time, status)
  - hunt_servers (id, ip, port, max_players, current_players, status)

API Endpoints:
  POST   /matchmaking/queue (join)
  DELETE /matchmaking/queue (leave)
  GET    /matchmaking/status (check status)

Network:
  - Notify players when match found
  - Send server IP + port
  - Send match info (hunt difficulty, behemoth, etc.)

Responsibilities:
  - Accept queue requests
  - Wait for sufficient players
  - Call matching algorithm
  - Select hunt server
  - Notify clients
  - Clean up on timeout
```

**EVIDENCE:**
- Hunt system requires player grouping
- Expects multiple hunts running simultaneously
- Typical MMO matchmaking pattern

**CONFIDENCE:** CONFIRMED

---

### 6. Hunt Instance (Game Server)

**CLIENT EXPECTATION:**
- Connect to specific server IP:port
- Spawn into hunt environment
- See teammates + enemies (behemoth)
- Can move, attack, use abilities
- Hunt ends when behemoth dies or time limit

**SERVER REQUIREMENT:**
```
Components:
  - Game server process (one per hunt)
  - World instance (hunt arena)
  - Behemoth entity (AI controlled)
  - Player character entities
  - Environmental hazards

Database:
  - hunt_sessions (id, start_time, end_time, difficulty, behemoth_id)
  - hunt_participants (id, hunt_id, character_id, damage_dealt, damage_taken)

Network (High-frequency):
  - Actor replication (30+ Hz)
  - Movement synchronization
  - Combat event broadcasting
  - Behemoth AI state
  - Environmental updates

Responsibilities:
  - Validate player connection
  - Spawn players
  - Manage behemoth AI
  - Calculate damage (authoritative)
  - Resolve combat
  - Track hunt progress
  - Generate loot
  - End hunt condition
  - Disconnect handling
```

**EVIDENCE:**
- "Hunt instances" explicitly required
- Combat system required
- Multiplayer gameplay
- Behemoth entities expected

**CONFIDENCE:** CONFIRMED

---

### 7. Entity/Behemoth System

**CLIENT EXPECTATION:**
- Behemoth is entity in world
- Has health, position, animations
- Responds to player attacks
- AI-controlled attacks/movement
- Dies when health reaches 0

**SERVER REQUIREMENT:**
```
Database:
  - behemoths (id, name, health_max, ai_type, difficulty)
  - behemoth_instances (id, hunt_id, behemoth_id, current_health, phase)
  - parts (id, behemoth_id, name, health_max) [breakable parts]

Components:
  - Behemoth AI system
  - Physics/collision
  - Animation state management
  - Part damage tracking

Network:
  - Behemoth position replication
  - Animation state broadcasting
  - Health updates
  - Part break events
  - Attack telegraphing

Responsibilities:
  - Spawn behemoth instance
  - Run AI loop (think + act)
  - Calculate damage taken
  - Manage health state
  - Handle part breaks
  - Broadcast state to players
  - Remove when dead
```

**EVIDENCE:**
- Game called "Dauntless" → hunt behemoths
- Combat system required
- Multiplayer targets behemoth
- AI-controlled enemies

**CONFIDENCE:** CONFIRMED

---

### 8. Combat System

**CLIENT EXPECTATION:**
- Player attacks with weapon
- Damage calculation happens server-side
- Health reduced
- Buffs/debuffs applied
- Status effects (burning, poison, etc.)

**SERVER REQUIREMENT:**
```
Database:
  - weapons (id, name, damage_min, damage_max, attack_speed)
  - abilities (id, name, damage, cooldown, effect)
  - status_effects (id, name, duration, effect_type)

Components:
  - Damage calculator
  - Hit validator
  - Effect applier
  - Cooldown tracker

Responsibilities:
  - Receive attack input from client
  - Validate attack (in range, cooldown, stamina)
  - Calculate damage (randomized, modifiers)
  - Check hit against behemoth
  - Apply damage to behemoth
  - Apply status effects
  - Broadcast damage event
  - Track DPS for rewards
```

**EVIDENCE:**
- Combat gameplay required
- Action game mechanics
- Server authority required (anti-cheat)
- Multiplayer coordination needed

**CONFIDENCE:** CONFIRMED

---

### 9. Inventory System

**CLIENT EXPECTATION:**
- Player has inventory of items
- Items include weapons, armor, consumables
- Equipment selected for hunt
- Inventory persists across sessions
- Can craft/combine items (possibly)

**SERVER REQUIREMENT:**
```
Database Tables:
  - inventory_items (id, character_id, item_id, quantity, equipped)
  - weapons (id, name, rarity, damage, perks)
  - armor (id, slot, name, rarity, defense, perks)
  - consumables (id, name, effect, stack_size)

API Endpoints:
  GET    /inventory/{character_id}
  POST   /inventory/{character_id}/equip
  POST   /inventory/{character_id}/unequip
  POST   /inventory/{character_id}/consume (use item)

Responsibilities:
  - Store item data
  - Track equipped items
  - Manage item quantities
  - Validate equipment before hunt
  - Update after hunt (loot)
  - Calculate derived stats (from gear)
```

**EVIDENCE:**
- Inventory system standard in MMOs
- Equipment loadouts required
- Progression tied to items
- Loot rewards from hunts

**CONFIDENCE:** CONFIRMED

---

### 10. Progression & Leveling

**CLIENT EXPECTATION:**
- Player character has level (1-50 or similar)
- Experience gained from hunts
- Skills/perks unlocked at milestones
- Battle pass or seasonal progression
- Multiple weapons/armor can level separately

**SERVER REQUIREMENT:**
```
Database:
  - character_progression (character_id, level, experience, points)
  - weapon_mastery (character_id, weapon_id, mastery_level, experience)
  - skill_tree (character_id, skill_id, unlocked)

API Endpoints:
  GET    /progression/{character_id}
  POST   /progression/{character_id}/claim-reward

Responsibilities:
  - Award experience after hunt
  - Calculate level ups
  - Unlock skills
  - Track mastery levels
  - Send progression updates
```

**EVIDENCE:**
- RPG progression expected
- Hunt rewards must feed progression
- Character advancement motivates play

**CONFIDENCE:** CONFIRMED

---

### 11. Persistence Layer

**CLIENT EXPECTATION:**
- All changes persist after logout
- No data loss on disconnect
- Rewards saved immediately after hunt
- Equipment choices saved

**SERVER REQUIREMENT:**
```
Database (Comprehensive):
  - accounts
  - characters
  - inventory_items
  - hunt_history
  - progression
  - equipment_loadouts
  - friends_list (optional)
  - blocked_players (optional)

Responsibilities:
  - Save on every change
  - Atomic transactions for multi-step operations
  - Backup/recovery procedures
  - Data validation on load
  - Concurrent access handling
```

**EVIDENCE:**
- Standard MMO requirement
- Unreal Server expects persistent data
- Hunt rewards must persist

**CONFIDENCE:** CONFIRMED

---

## Interaction Flows

### Login Flow
```
CLIENT                          SERVER
  |
  1. [Email/Password]
  +--[POST /auth/login]------->|
  |                            | [Hash password, verify]
  |<--[Auth Token]-------------+ [Create session]
  |
  2. [Query Profile]
  +--[GET /profile]---------->|
  |   (with token)            |
  |<--[Character Data]--------+
  |
  3. [Enter Lobby]
  +--[Connect to Lobby Server]->|
  |                             | [Spawn entity]
  |<--[Welcome + World State]--+
```

### Hunt Flow
```
CLIENT/PARTY              MATCHMAKING              HUNT SERVER
  |
  1. [Find Hunt]
  +--[POST /matchmaking/queue]->|
  |                             | [Queue]
  |
  [Wait...]
  |
  |<--[Match Found]------[Server IP + Port]
  |
  2. [Connect]
  +--[Connect UDP]-----[Hunt Server]
  |                          |
  |                     [Validate token]
  |                     [Spawn players]
  |                     [Spawn behemoth]
  |                     [Start replication]
  |
  |<--[Welcome + World]---------+
  |
  3. [Combat Loop]
  +--[Movement/Attack]--[Continuous]->|
  |                                    | [Update state]
  |<--[Replication Stream]-----[Continuous]
  |
  [Hunt until complete...]
  |
  4. [Hunt End]
  +--[Disconnect]
  |                                    | [Calculate loot]
  |                                    | [Save results]
  |
  |<--[Results/Rewards]
  |
  5. [Back to Lobby]
  +--[Connect to Lobby]
```

---

## Summary Table

| System | Component | Client-Side | Server-Side | Persistence | Network |
|--------|-----------|------------|-------------|-------------|---------|
| **Auth** | Login | UI | Token issuer | Accounts DB | HTTPS |
| **Profile** | Character data | Display | Storage | Characters DB | HTTPS/TCP |
| **Lobby** | Ramsgate | Entity rendering | Entity manager | World state | UDP |
| **Party** | Grouping | UI | Membership tracker | Party DB | TCP/HTTPS |
| **Matchmaking** | Queue | Status UI | Matcher | Queue DB | HTTPS/TCP |
| **Hunt** | Game loop | Game engine | Authoritative server | Hunt results | UDP |
| **Entities** | Behemoths | Rendering | AI + physics | Progression | UDP |
| **Combat** | Attacks | Input | Resolver | Loot | UDP |
| **Inventory** | Items | Display | Storage | Items DB | TCP/HTTPS |
| **Progression** | XP/Levels | Display | Tracker | Progress DB | TCP/HTTPS |

---

## Technology Recommendations

Based on client expectations:

### Backend Stack
- **Language:** Python (Flask/FastAPI) or C++ (Unreal plugin)
- **Game Server:** Unreal Engine (match client)
- **Database:** PostgreSQL (robust, multi-client)
- **Message Broker:** Redis (party/matchmaking state)
- **API Framework:** REST + WebSocket (notifications)

### Deployment
- **Lobby:** Single persistent server instance
- **Hunt:** Spawned on-demand, destroyed on completion
- **Scaling:** Horizontal (multiple hunt servers)

---

## Unknown Specifics

| Question | Impact |
|----------|--------|
| Exact hunt duration | Affects server resource allocation |
| Max party size | Affects hunt instance size |
| Behemoth AI complexity | Affects CPU per hunt |
| Loot table format | Affects reward generation |
| Guild/clan system | Affects social features |
| Trading system | Affects inventory operations |
| Cosmetics | Affects client->server sync |

---

**Research Status:** ⚠️ Reconstructed from client analysis
**Confidence:** LIKELY (not confirmed from server source)
**Next Step:** Network analysis to determine actual architecture

