# Unreal game-server static evidence

Date: 2026-09-20

This is a read-only static-analysis note for the locally supplied retail client. It records evidence relevant to reproducing an independently implemented game server. It does not modify the client, capture credentials, contact production services, or describe an anti-cheat bypass.

## Build examined

- Executable: `Dauntless/Archon/Binaries/Win64/Dauntless-Win64-Shipping.exe`
- SHA-256: `934325ACECF64E19A01F70F72DCDCEBD68CFB12F11A812CD551C608AC16CEA34`
- Windows version resource: `5.1.1.0`
- Embedded source paths contain `D:\phx-archon_release_2.1.1\Engine\...`. This is strong evidence for the internal branch name but is not by itself an exact public Unreal version identifier.
- The shipped manifest dates this executable `2024-12-18T01:36:47.219Z`.

Method: bounded extraction of printable ASCII strings from the executable, inspection of Windows version metadata, and inspection of the shipped file manifests. String presence proves that the symbol/text is included in this build; it does not prove that a path executes at runtime or reveal serialization layouts.

## High-confidence network architecture

The client contains the normal Unreal network-driver and control-channel stack plus game-specific orchestration around it:

1. A matchmaking layer selects a session/server. The UFS manifest explicitly names `Archon/Plugins/PhoenixMatchmaker/PhoenixMatchmaker.uplugin`.
2. Party membership is reserved through Unreal party beacons. Concrete symbols include `APartyBeaconClient::RequestAddOrUpdateReservation`, `APartyBeaconHost::ProcessReservationUpdateRequest`, `APartyBeaconHost::UpdatePartyReservation`, `ServerReservationRequest`, `ServerUpdateReservationRequest`, and `ServerReconnectRequest`.
3. The client travels to an Unreal game world. Relevant symbols include `ClientTravel`, `ServerTravel`, `StartTravelToMission`, `StartTravelToCity`, `TravelToCompletedCityMatchmakingSession`, `CompleteTravelToMission`, and `bUseSeamlessTravel`.
4. The game world uses actor replication/RPC. The manifest includes the engine ReplicationGraph plugin, and the executable includes `/Script/ReplicationGraph`, `ReplicationGraph`, `ClassReplicationInfo`, and game-specific `ArchonConnectionAlwaysRelevantNodePair`.
5. The server is authoritative for important gameplay and persistence mutations. Examples include server RPCs for inventory consumption/crafting, loadout assignment/cell changes, portal validation, supply-crate use, and pet evolution, paired with client RPCs for inventory refresh, item grants, errors, encounter updates, and rewards.

This means the Python HTTP API in this repository is a possible control-plane/backend component, but it is not the game-server data plane expected by the retail client. A compatible implementation would also need an Unreal-wire-compatible server with the correct map, replicated class, property, RPC, package, and network-version contracts.

## Connection and session clues

### Net drivers and transport

Observed strings include `GameNetDriver`, `PendingNetDriver`, `BeaconNetDriver`, `NetDriverDefinitions`, `DriverClassName`, `NetConnectionClassName`, `InitialConnectTimeout`, `ConnectionTimeout`, `MaxClientRate`, and `MaxPacket`. `EPingType::UDPQoS`, `ServerQosRequest`, and `ClientQosResponse` are direct evidence that UDP QoS probing is represented in the build.

The evidence supports Unreal networking and UDP QoS, but it does **not** establish the production game port, beacon port, socket subsystem chosen for gameplay, or whether every deployed session uses direct UDP rather than an EOS relay/P2P path. No configured `Port=`, `BeaconPort=`, or `7777` value was found in the inspected loose configuration or the targeted executable-string pass. Existing documentation that states port 7777 is speculation and must not be treated as a discovered value.

### Matchmaking and reservations

Observed game modes include city, escalation, event, FTUE, gauntlet, hunting ground, legacy hunt, mission, romp, training ground, and trial. Matchmaking types include city, open, and reserved. Reservation outcomes include accepted, duplicate, bad session ID, incorrect player count, party limit, banned, cross-play restriction, and existing-player conflicts.

These names imply a two-stage join flow: control-plane matchmaking/session assignment, then a beacon reservation/reconnect transaction before or alongside world travel. They do not expose the Phoenix Matchmaker HTTP request or response schemas.

### Reconnect

`ArchonReconnectClientData`, `ClientReconnectStart`, `ClientReconnectResponse`, `ServerReconnectRequest`, `EReconnectResult`, and `bEnableReconnectBeacon` indicate an explicit reconnect path. A replacement server should preserve a stable session/player identity across a temporary network loss and retain enough reservation state to validate a rejoin.

### Travel

The client contains absolute, relative, and partial Unreal travel types; city and mission travel operations; seamless-travel state; and the usual invalid URL/package/version failure states. No fixed production address was found. The actual destination is assembled at runtime from matchmaking/session data rather than embedded as a fixed URL.

### Recovered runtime travel template

A deeper offset-aware pass recovered the exact UTF-16LE connect-string format at decimal file offset 105601408:

```text
%s:%d?ticket=%s?gameSessionId=%s?EncryptionToken=%s
```

Nearby strings identify this as the Phoenix online-session `GetResolvedConnectString` path (`invalid session info for session %s in getresolvedconnectstring()` at 105601120 and `Invalid session info in GetResolvedConnectStringInternal()` at 105601520). Separately, the game session client logs `Initiating client travel to session: %s with URL: %s` at 115656592. This is direct evidence that the matchmaking/session layer constructs a runtime Unreal travel destination from host, port, ticket, game-session ID, and encryption token.

The format establishes option names and ordering, but not token formats, issuers, cryptography, concrete host/port, map package, or whether further options are appended. Phoenix matchmaking result vocabulary adjacent in the binary includes `gameSessionId`, `host`, `port`, `gameArgs`, `buildId`, `gameMode`, and `gameType` (105572824-105572968). Candidate polling logs `GameSessionId: %s Host: %s:%d` at 105597376.

## Handshake and compatibility clues

The executable contains Unreal close/failure reasons including:

- `OutdatedClient` and `OutdatedServer`
- `EncryptionTokenMissing`
- `PreLoginFailure`
- `ControlChannelEndianCheck`
- `ControlChannelMessageFail` and payload/unknown-message variants
- `ControlChannelEasyAntiCheatSessionFail`
- beacon authentication, invalid-ID, control-flow, packet-parse, and NetGUID-ack failures

It also contains the Unreal login format string `LOGIN %s %s`, `AArchonGameMode::Login`, `AArchonGameMode::GameWelcomePlayer`, `BuildUniqueId`, `GetMatchmakingBuildId`, and the standard control-channel/player-channel concepts. This strongly indicates that successful admission is more than opening a UDP socket: the client and server must agree on Unreal network compatibility, package/map identity, the control-message sequence, player identity/options, and any enabled encryption/auth handler.

The static pass did not recover an exact network-version integer, compatible changelist, encryption-token schema, packet-handler configuration, or game-specific pre-login option layout. TLS/OpenSSL `handshake` strings in the executable mostly belong to generic bundled HTTP/TLS libraries and must not be confused with the Unreal UDP handshake.

Beacon admission has more concrete generic Unreal evidence. At offsets 103117568-103118080 the sequence is `NMT_Hello`, network-version comparison, encryption-token checks, `NMT_Login`, then a login log with request, user ID, and platform. `AuthTicket=%s` occurs at 103113592, while the login-side key `AuthTicket` occurs at 103118272. Reservation state contains `DestSessionId`, `PendingReservation`, `RequestType`, `Token`, `TokenBytes`, and `ValidationInfo` at 103054016-103054160. These strings establish likely beacon/control-message inputs, but not their binary serialization or game-specific validation rules.

Reservation logs add an observable state model: `RequestReservationUpdate` requires both a connect-info string and session ID (103135920); the host logs session ID, party leader, party size, and remote address when processing reservations (103142944-103143488). No fixed beacon port was recovered; only the configuration key `BeaconPort=` at 103117456.

## Replication and RPC surface samples

The following game-specific names are useful anchors for later lawful protocol observation or clean-room schema work:

- Character: `ServerSetClientAuthoritativeCustomMovement`, `ServerUseSupplyCrate`
- Inventory: `ServerConsumeItem`, `ServerCraftItemFromCatalogData`, `ServerDustItemWithQuantity`, `ServerHandleInventoryHashMismatch`, `ClientQueryInventory`, `ClientRefreshInventory`, `ClientItemCustomDataReplicated`, `OnRep_ReplicatedItems`
- Loadout: `ServerAssignItem`, `ServerInfuseCell`, `ServerRemoveCell`, `ServerSetItemPart`, `ServerSetBannerCustomizationData`, `ClientRaiseLoadoutServiceError`
- Player controller/portal: `ServerDoubleCheckCanUserInteractWithPortal`, `ServerReadyToEnterPortal`, `ServerUsePortalKey`, `ClientDoubleCheckCanUserInteractWithPortalResult`
- Mission lifecycle: client notifications for island gameplay start, encounter start/progress/end, behemoth killed, rewards granted, player joined/left, and server shutdown warning

Names alone do not reveal parameters, reliability, ownership rules, channel indexes, field conditions, RepNotify ordering, or NetGUID/export dependencies. Implementing similarly named JSON endpoints would not make them compatible with Unreal RPC serialization.

## Dedicated-server clues and limits

The binary has numerous dedicated-server flags and branches, including `bAllowTickOnDedicatedServer`, `bEnablePhysicsOnDedicatedServer`, `bListenOnDedicatedServer`, `bHandleDedicatedServerReplays`, `bSimulateSkeletalMeshOnDedicatedServer`, and `bStripFromClientBuilds`. Game-specific authoritative RPC implementations and `AArchonGameMode` login/welcome functions further support a dedicated authoritative server design.

However, the supplied folder contains a `WindowsClient` build and no `WindowsServer` executable, server target, server PDB, or loose server configuration. The client executable cannot be assumed to contain all server-only classes or cooked server content. A full compatible server cannot be reconstructed from the current symbols alone.

## Service-role correction

The build contains PlayFab-named assets/plugin references, EOS SDK/subsystem references, and a PhoenixMatchmaker plugin. Static presence does not prove the earlier documentation claim that PlayFab is the primary transport or that "95% of game data" goes through PlayFab. The direct game-session evidence points to an Unreal replicated server reached through matchmaking/travel. PlayFab/EOS/Phoenix may perform identity, economy, telemetry, matchmaking, allocation, or session discovery roles, but their exact responsibility requires runtime evidence.

## Evidence still required

For an interoperable clean-room server, the next useful artifacts are authorized, user-owned runtime logs/captures from an ordinary successful client session, with credentials and personal data redacted:

- DNS and destination metadata to separate backend HTTPS, matchmaking, QoS, beacon, and game traffic
- The runtime travel destination shape (not production secrets)
- Unreal initial packet/control-message ordering and close reason
- Actual network/build compatibility values
- Map/package name and game mode selected for city versus hunt
- Reservation and reconnect timing/state transitions
- Replicated class/field export information and RPC parameter layouts

These must be versioned against the executable hash above. Evidence from another client build may be wire-incompatible.

## Bottom line

The client expects a layered system: backend identity/data and matchmaking, Unreal beacon reservation/reconnect, Unreal travel, then an authoritative replicated Unreal game session. The most immediate project correction is to stop treating PlayFab REST emulation as the game server itself. The unknowns blocking compatibility are the runtime-assigned destination, control-channel admission contract, network/package version, reservation payload, and replicated gameplay schemas—not the existence of generic account CRUD endpoints.
