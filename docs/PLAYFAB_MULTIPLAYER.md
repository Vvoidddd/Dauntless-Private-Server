# PlayFab Multiplayer Integration Research

This document describes a supported, clean-room route from this HTTP prototype to a multiplayer game stack using Microsoft PlayFab. It is based on official Microsoft and PlayFab sources. PlayFab can host and orchestrate a game server executable that the developer owns; it does not supply Dauntless gameplay logic, maps, Unreal replication code, proprietary service contracts, or credentials.

## Capability boundary

PlayFab Multiplayer Servers (MPS) is managed hosting for a custom Windows or Linux dedicated-server build. The build must implement the game's authoritative simulation and integrate the PlayFab Game Server SDK (GSDK). MPS then provides Azure-based placement, scaling, lifecycle management, endpoint allocation, and logs. See the [MPS overview](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/) and [server terminology](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/server-terms).

PlayFab cannot make the retail Dauntless client compatible with this project. It does not reproduce the retail client's proprietary authentication, HTTP, serialization, gameplay, or Unreal networking contracts. Removing or omitting EAC does not fill those gaps. A supported implementation therefore requires an owned, clean-room client and dedicated server (or source and authorization from the rights holder). It must not use another title's PlayFab Title ID, secrets, tokens, or services.

## Multiplayer Servers and GSDK

A PlayFab multiplayer build is the complete server executable and its dependencies, integrated with GSDK. GSDK communicates with the PlayFab VM agent and reports the server lifecycle and health. A normal lifecycle progresses through initialization and standby, allocation/active play, and termination. The server should accept players only after it is ready and exit cleanly when terminated. The [authoring guide](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/author-a-game-server-build) explains the build requirement.

Build configuration selects the VM type, process/container settings, exposed ports, assets, certificates, metadata, and regional capacity. Each enabled region has a standby target and maximum-server value. Standby instances reduce allocation latency but consume compute. Exact configuration fields are documented in [Build definition and configuration](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/build-definition).

Use a build alias as the stable deployment target instead of embedding a build ID in clients or queue configuration. An alias permits gradual server-build replacement and rollback. Microsoft also recommends multiple acceptable regions and build aliases for launch readiness in its [MPS best-practices checklist](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/best-practices).

Server allocation can be automatic through matchmaking or explicit through `RequestMultiplayerServer`. An explicit request includes a unique session ID, ordered preferred regions, and either a build ID or alias. It may include an initial-player allowlist and a session cookie (maximum 8 KB). The successful response provides the address and named ports the clean-room client uses to connect. See the current [RequestMultiplayerServer REST reference](https://learn.microsoft.com/en-us/rest/api/playfab/multiplayer/multiplayer-server/request-multiplayer-server?view=playfab-rest).

Keep developer secret keys and administrative credentials on a trusted backend. Never commit them or distribute them in a game client. Environment configuration should contain only deployment-specific values such as `PLAYFAB_TITLE_ID`, `PLAYFAB_BUILD_ALIAS_ID`, and `PLAYFAB_QUEUE_NAME`; secrets need an external secret store in production.

## Matchmaking, Lobby, and Party

These products have distinct responsibilities:

- **Matchmaking** groups compatible tickets in a named queue. Queue rules can cover mode, build version, skill, team composition, and region latency, and can relax with wait time. A player can be in only one ticket at a time. See the [matchmaking overview](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/matchmaking/).
- **MPS allocation from matchmaking** binds a queue to a build or build alias and requires a region-selection rule. After a match and allocation, `GetMatch` exposes the allocated endpoint. Match members are passed to GSDK as initial players, but arbitrary ticket attributes are not automatically passed. See [Integrating matchmaking with MPS](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/matchmaking/multiplayer-servers).
- **Lobby** is transient coordination and discovery state. It can carry server connection information and player configuration, and arranged lobbies can be created for matched players. Persistent progression still belongs in a durable backend. The intended composition and backfill flow are documented in [Use Lobby and Matchmaking Together](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/lobby/lobby-and-matchmaking).
- **Party** provides authenticated, encrypted low-latency data communication, relay/direct connectivity, voice, text, and QoS. It is not a replacement for an authoritative dedicated game simulation. Microsoft recommends MPS for authoritative game logic and Party for communications in that architecture. See the [PlayFab Party overview](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/networking/).

For a simple private test, matchmaking and Party are optional. A trusted backend can explicitly allocate an MPS session for a known group and return its endpoint. Add queue rules, Lobby, backfill, and Party only when their behavior is needed.

## Unreal integration

The PlayFab Online Subsystem integrates Lobby, Matchmaking, and Party with Unreal's standard online interfaces. It complements rather than replaces the platform's native online subsystem. See Microsoft's [PlayFab OSS overview](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/networking/party-unreal-engine-oss-overview), the current [PlayFab for Unreal overview](https://learn.microsoft.com/en-us/gaming/playfab/sdks/unified-unreal/overview), and the official [PlayFabMultiplayerUnreal repository](https://github.com/PlayFab/PlayFabMultiplayerUnreal).

Dedicated Unreal servers use the GSDK Unreal plugin. The plugin offers C++ and Blueprint-facing APIs, but the Unreal project itself must be a C++ project. Follow the [Unreal GSDK guide](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/server-sdks/unreal-gsdk/) and obtain GSDK from the official [PlayFab/gsdk repository](https://github.com/PlayFab/gsdk). Pin tested releases instead of tracking an unpinned branch.

The Python API in this repository can remain a local account/progression control plane during development. A future PlayFab provider should sit behind an explicit allocation/matchmaking interface so local tests do not require cloud credentials. It should not pretend to implement PlayFab wire compatibility.

## LocalMultiplayerAgent workflow

LocalMultiplayerAgent (LMA) runs a GSDK-integrated server locally and mocks the platform lifecycle without a cloud allocation. It is the cheapest and fastest validation loop before uploading a build. Microsoft documents process and container modes in the [LMA overview](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/LocalMultiplayerAgent/local-multiplayer-agent-overview).

The recommended loop is:

1. Build an owned Unreal C++ dedicated-server target and integrate GSDK.
2. Define named gameplay ports and local `MultiplayerSettings.json` configuration.
3. Run the server through LMA in process mode first.
4. Verify initialization, standby, activation, player handling, graceful termination, logs, and crash behavior.
5. Test the clean-room client against `127.0.0.1` and the configured port.
6. Repeat in the same container form intended for MPS, if applicable.
7. Upload only after local lifecycle and connection tests pass.

LMA mocks orchestration, not game networking. A successful lifecycle test does not prove gameplay correctness, load capacity, or retail-client compatibility.

## Cost and quota cautions

PlayFab pricing is consumption based and changes over time, so this repository should not hard-code dollar estimates. MPS meters VM instance time—including standby/fragmentation overhead—and network egress. Matchmaking and Lobby meter API requests and delivered real-time messages. Party separately meters connected/speaking minutes, optional cognitive/moderation features, and relay egress. Consult the official [pricing meters](https://learn.microsoft.com/en-us/gaming/playfab/pricing/meters/meters) and [pricing overview](https://learn.microsoft.com/en-us/gaming/playfab/pricing/pricing-overview) before enabling cloud resources.

MPS includes limited evaluation capacity. Production capacity is constrained by per-title core quotas across VM families and regions; increases may require review and should be requested well before a launch or load event. See [Managing Server Cores Quota](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/quota-changes). Keep standby at zero outside scheduled testing until allocation latency is being measured, then size it from observed startup time and allocation rate as described in [Scaling standby](https://learn.microsoft.com/en-us/gaming/playfab/multiplayer/servers/scaling-standby).

## Clean-room deployment roadmap

1. **Define the protocol:** document an owned client/server protocol, authoritative state model, session admission token, and disconnect/reconnect rules.
2. **Create the game pair:** implement a minimal Unreal C++ client and dedicated server with one replicated test map and no dependency on retail Dauntless binaries or services.
3. **Integrate GSDK:** report lifecycle, read session ID/initial players/session cookie, emit structured logs, and shut down cleanly.
4. **Validate locally:** automate LMA startup, allocation-state simulation, endpoint connectivity, invalid-player rejection, crash recovery, and termination tests.
5. **Add a provider boundary:** retain the local allocator for tests and add a server-side PlayFab allocator configured only through environment/secret storage.
6. **Deploy one development build:** use one low-cost region, zero or scheduled standby, conservative maximum capacity, and a build alias.
7. **Connect end to end:** authenticate the clean-room client, allocate through the trusted backend, return endpoint plus short-lived admission data, and validate it on the dedicated server.
8. **Add matchmaking:** create a development queue with game-version equality and latency-based region selection; bind it to the build alias.
9. **Add Lobby/Party selectively:** use Lobby for group coordination and server details; use Party only for communication/voice requirements not served by Unreal networking.
10. **Harden before wider use:** load-test server packing, request quota, deploy multiple regions, protect secrets, add metrics/alerts, archive logs and dumps, rehearse alias rollback, and set spending alerts.

This roadmap produces a supported PlayFab-hosted clean-room game. It does not turn the retail Dauntless executable into that client.
