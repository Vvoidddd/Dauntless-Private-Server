# TODO

## PHASE 0: CLIENT RESEARCH

### Phase 0 - Complete
- [x] Inventory client files
- [x] Identify game engine (Unreal Engine 5)
- [x] Identify main executable (Dauntless-Win64-Shipping.exe)
- [x] Identify launcher (start_protected_game.exe)
- [x] Document DLLs and dependencies (Boost, EOS SDK, etc.)
- [x] Identify configuration system (EasyAntiCheat Settings.json)
- [x] Determine online services (Epic Online Services)
- [x] Identify compiler and platform (MSVC 142, Win64)

### Phase 0.1 - Complete
- [x] Determine game technology (Unreal Engine 5)
- [x] Document evidence (directory structure, binaries)
- [x] Identify networking libraries (Boost, Unreal Replication Graph)
- [x] Identify online services (EOS SDK)

### Phase 0.2 - Complete
- [x] Executable analysis (Dauntless-Win64-Shipping.exe, start_protected_game.exe)
- [x] DLL analysis (EOSSDK, Boost libraries, graphics DLLs)
- [x] Debug symbols identified (PDB files available)
- [x] Document dependencies and purposes

### Phase 0.3 - In Progress
- [ ] Find server configuration files
- [ ] Extract server URLs from config/binary
- [ ] Find API endpoint references
- [ ] Document matchmaking endpoints
- [ ] Document authentication endpoints
- [ ] Extract environment variables
- [ ] Find port configurations

### Phase 0.4 - In Progress
- [ ] Network traffic capture (Wireshark)
- [ ] Identify EOS endpoints
- [ ] Determine game server ports
- [ ] Document protocol handshake
- [ ] Identify packet structure (if possible)
- [ ] Determine encryption methods

### Phase 0.5 - Not Started
- [ ] Search for game system references (player, character, inventory, etc.)
- [ ] Analyze gameplay systems in asset paks
- [ ] Document quest system
- [ ] Document combat system
- [ ] Document progression system
- [ ] Document hunting system

### Phase 0.6 - In Progress
- [x] Build expected server architecture model
- [ ] Validate assumptions against actual implementation
- [ ] Identify gaps in understanding
- [ ] Document uncertainty levels

---

## STAGE 1: SERVER SKELETON

- [x] Create project directory structure
- [x] Initialize Python environment (FastAPI)
- [x] Create main server entry point
- [ ] Set up logging system
- [x] Create configuration management
- [x] Document architecture

---

## STAGE 2: DATABASE

- [x] Choose database (SQLite for the local milestone; production choice remains open)
- [ ] Design schema
  - [x] accounts table
  - [x] characters table (local simulated-gameplay scope)
  - [x] sessions table
  - [x] inventory_items table (local simulated-gameplay scope)
  - [x] parties table (local simulated-gameplay scope)
  - [ ] progression table
- [ ] Create migration scripts
- [ ] Set up connection pooling
- [x] Write database utility functions for the local SQLite milestone

---

## STAGE 3: AUTHENTICATION

- [x] Implement password hashing (scrypt; Argon2id remains a possible future migration)
- [x] Create account registration endpoint
- [x] Create login endpoint
- [x] Implement session token generation
- [x] Create token validation function
- [x] Test account creation flow
- [x] Test login flow
- [x] Test token expiry

---

## STAGE 4: DISCORD BOT

- [ ] Create Discord bot
- [ ] Implement /createaccount command
- [ ] Create modal form for registration
- [ ] Validate form inputs
- [ ] Link Discord ID to game account
- [ ] Send confirmation message
- [ ] Test Discord integration

---

## STAGE 5: LAUNCHER LOGIN

- [ ] Create launcher UI (Tkinter or PyQt)
- [ ] Add email field
- [ ] Add password field
- [ ] Implement login button
- [ ] Send credentials to server
- [ ] Receive and store auth token
- [ ] Display server status
- [ ] Display online player count
- [ ] Test launcher flow

---

## STAGE 6: CLIENT/SERVER CONNECTION

- [ ] Create Unreal Engine client connection code
- [ ] Parse launcher config file
- [ ] Read auth token from launcher
- [ ] Connect to game server
- [ ] Implement handshake protocol
- [ ] Test connection
- [ ] Test disconnection

---

## STAGE 7: PLAYER SESSION

- [ ] Implement session creation
- [ ] Track player connection state
- [ ] Implement character spawning
- [ ] Create lobby entity for player
- [ ] Test player join
- [ ] Test player disconnect

---

## STAGE 8: PLAYER STATE SYNCHRONIZATION

- [ ] Implement actor replication
- [ ] Replicate player position
- [ ] Replicate player rotation
- [ ] Replicate player animations
- [ ] Broadcast state to other players
- [ ] Test multi-player synchronization

---

## STAGE 9: PARTY SYSTEM

- [ ] Create party data model
- [ ] Implement party creation
- [ ] Implement party join
- [ ] Implement party leave
- [ ] Implement party disband
- [ ] Broadcast party updates
- [ ] Test party operations

---

## STAGE 10: LOBBY/WORLD

- [ ] Create persistent lobby world
- [ ] Implement NPC spawning
- [ ] Create vendor system
- [ ] Implement chat system
- [ ] Test lobby interactions

---

## STAGE 11: HUNT INSTANCE

- [ ] Create hunt server component
- [ ] Implement hunt session creation
- [ ] Implement player spawning in hunt
- [ ] Create behemoth spawning
- [ ] Implement hunt termination
- [ ] Test hunt startup/shutdown

---

## STAGE 12: ENTITY SYNCHRONIZATION

- [ ] Implement entity replication
- [ ] Synchronize behemoth state
- [ ] Synchronize player state in hunt
- [ ] Test multi-entity scenarios

---

## STAGE 13: COMBAT

- [ ] Implement damage calculation
- [ ] Implement hit detection
- [ ] Implement status effects
- [ ] Implement cooldown tracking
- [ ] Test damage application

---

## STAGE 14: INVENTORY

- [ ] Implement inventory storage
- [ ] Implement equipment system
- [ ] Implement loadout selection
- [ ] Implement loot generation
- [ ] Test inventory operations

---

## STAGE 15: PROGRESSION

- [ ] Implement XP tracking
- [ ] Implement level system
- [ ] Implement skill unlocks
- [ ] Implement weapon mastery
- [ ] Test progression flow

---

## STAGE 16: PERSISTENT MULTIPLAYER TESTING

- [ ] Create comprehensive integration test
- [ ] Test full flow: Discord → Database → Launcher → Auth → Game → Hunt → Rewards
- [ ] Test with multiple players simultaneously
- [ ] Test party hunting
- [ ] Test disconnection recovery
- [ ] Test data persistence
- [ ] Performance testing
- [ ] Stability testing

---

## DOCUMENTATION

- [x] Write ARCHITECTURE.md
- [ ] Write DEVELOPMENT_PLAN.md
- [ ] Write DATABASE.md
- [ ] Write NETWORKING.md
- [ ] Write AUTHENTICATION.md
- [ ] Write LAUNCHER.md
- [ ] Write DISCORD.md
- [ ] Write GAME_SERVER.md
- [ ] Write HUNT_SYSTEM.md
- [x] Write TESTING.md
- [x] Write SECURITY.md
- [x] Write KNOWN_LIMITATIONS.md

---

## CURRENT STATUS

**Phase:** Local HTTP milestone plus ongoing research
**Last Updated:** 2026-08-30
**Verified:** The local HTTP milestone has isolated API, authentication, configuration, simulated-gameplay, and tooling coverage; 27 tests passed in 3.25 seconds on 2026-08-30.
**Blockers:** Proprietary-client compatibility remains unverified and gated; there is no Unreal networking implementation.
**Next Action:** Add logging and migration/versioning support, then extend only evidence-backed local features. Do not treat inferred protocols as confirmed.

