# Static service-call inventory (2026-09-20)

Scope: read-only inspection of the locally supplied December 2024 Windows client. No client files were changed and no live services were contacted. Offsets below are decimal file offsets in `Dauntless/Archon/Binaries/Win64/Dauntless-Win64-Shipping.exe` (151,448,856 bytes; SHA-256 `934325ACECF64E19A01F70F72DCDCEBD68CFB12F11A812CD551C608AC16CEA34`). A printable string proves presence, not runtime execution or an HTTP contract.

## What is actually observed

### Service/domain clues

| Offset | String | Narrow conclusion |
|---:|---|---|
| 105631552 | `.playfabsandbox.com` | Code can form a PlayFab sandbox-style host name. |
| 105631576 | `.playfabapi.com` | Code can form a PlayFab production-style host name. |
| 127686672 | `graphql.epicgames.com` | Epic GraphQL host is embedded. The operation names/documents are not exposed beside it as plain strings. |
| 107164864 | `errors.com.epicgames.oss.chat` | Epic chat error namespace is embedded. |
| 107178328 | `errors.com.epicgames.oss.identity` | Epic identity error namespace is embedded. |
| 107187688 | `errors.com.epicgames.oss.gameservicemcp` | Epic game-service/MCP error namespace is embedded. |
| 107189888 | `errors.com.epicgames.oss.users` | Epic users error namespace is embedded. |

No exact PlayFab REST path such as `/Client/GetCatalogItems`, title ID, complete PlayFab hostname, Phoenix HTTP route, GraphQL document, or request JSON body was found as a printable executable string. Therefore the endpoint lists in older research notes are examples/guesses, not recovered Dauntless calls.

The UFS manifest identifies packaged plugin descriptors at `Manifest_UFSFiles_Win64.txt:10` (`PhoenixMatchmaker`) and line 15 (`PlayFab`). The descriptors are manifest entries, not loose source or protocol definitions.

### Authentication and connection clues

| Offset | String |
|---:|---|
| 113265696 | `TryEpicAutomaticLoginWithIdAndPassword` |
| 113271416 | `CharacterAuthToken` |
| 113301896 | `StartLoginWithAuthToken` |
| 113301920 | `StartLoginWithDummy` |
| 113301944 | `StartLoginWithEmail` |
| 109962080 | `bDisableMatchMakerAuth` |

These names indicate multiple application login entry points and a character/game-server auth token concept. They do not reveal field formats, token issuers, signing, or the order in which the methods run. `bDisableMatchMakerAuth` is only a reflected/configurable name; its presence does not establish that it is enabled or that changing it is sufficient for connection.

The EAC settings file contains `productid=prod-jackal`, `sandboxid=jackal`, and deployment `53565ba467df4edbb6f5a3d939a8b4f2`. These configure EAC/EOS anti-cheat packaging and must not be relabeled as a PlayFab title ID or a complete general EOS application configuration.

### EOS SDK surface linked into the build

The executable imports/references these relevant EOS operation families at offsets 139025118-139033892:

- Auth: `EOS_Auth_Login`, `Logout`, `LinkAccount`, `DeletePersistentAuth`, `CopyUserAuthToken`, login-status queries/notification.
- Connect: `EOS_Connect_Login`, `CreateUser`, external-account and product-user mapping queries, auth-expiration notification.
- Lobbies: create/join/leave/update/kick/invite/search plus lobby/member notifications and RTC-room lookup.
- Sessions: create/update/start/end/destroy/join, register/unregister players, invite and search.
- P2P: send/receive packet, connection request/closed notifications, accept/close.
- Anti-cheat client: begin/end session, poll status, receive server message, and callback registration for messages destined for the server.

This is stronger evidence for SDK capability than guessed HTTP paths, but an imported SDK symbol alone still does not prove every operation is used in a normal Dauntless session. EOS SDK calls also do not imply that the client directly calls made-up paths like `/auth/device` or `/matchmaking/find`.

### Phoenix backend operation names

The shipping binary exposes a useful application-level call inventory:

- Cohorts: `FOnlineCohortsPhoenix::QueryCohorts` (105506720).
- Escalation: get/set seasonal escalation (105511000, 105511352).
- Gauntlet: get season, progression, access, leaderboard, personal levels and guild rewards; post success and claim guild rewards (105519856-105522216).
- Trials leaderboard: `QueryTrialsLeaderboards` (105549008).
- Loadouts: get active/all/slot count; set persistent/slot/active slot; unlock slots (105551640-105552440).
- Mailbox/surveys: claim message parcel, submit survey reply, claim survey reward (105556096-105556456).
- Progression: query configuration/progression/objective(s)/track; grant purchase/progression/objectives/unclaimed rewards; delete and confirm rank; obtain rewards between levels (105586968-105593360).
- Store: get lootboxes/details and draw lootbox, including `ServerDrawLootbox` (105610456-105611312).

Related reflected client/server RPC names include `ClientQueryInventory`, `ClientRefreshInventory`, `ServerConsumeItem`, `ServerCraftItemFromCatalogData`, `ServerDustItemWithQuantity`, `ServerUnlockAsTransmog`, `ServerAddItemProgressionXPFromItems`, `ServerAddWeaponTalentXPFromItemsById`, `ServerQueryProgressInTrack`, `ServerQuerySlotCount`, and reservation-beacon add/update/cancel/reconnect calls. These are Unreal function names, not HTTP routes.

## Request/error type clues

Observed enums provide likely backend operation vocabulary:

- `ELoadoutServiceOperation`: `QuerySlotCount`, `SetActiveSlot`, `CommitSlotData`, `CommitPersistentData`.
- `ELoadoutRequestError`: missing slot data, slot count exceeded/unchanged, slot not unlocked, process failure, unknown.
- `EGuildRequestType`: validate/create/get/invites/invite/kick/leave/disband/promote/demote/accept/decline.
- `ELinkedSlayerRequestType`: get links/invites, send/cancel/accept/decline invite.
- Party results include `Failed_InMatchmaking`, `Failed_NotLeader`, `Failed_NotSelf`, and `Failed_UnknownPlayer`.
- Reservation request types include new/existing session reservation, reconnect, add/update, remove members, and abandon.

These are good candidates for model/test names in a clean-room backend, but serialization names and wire values remain unknown.

## Corrected architecture inference

The defensible model is: EOS SDK is present for Epic identity/connect/social/session/P2P functions; a Phoenix-specific online subsystem exposes progression, loadout, store, guild-like, mailbox, and event operations; PlayFab-named domains and catalog data types/plugins are present; and Unreal networking/RPC and party reservation code is present. Static strings do **not** establish that “95% of data goes through PlayFab,” that EOS matchmaking returns a server at a particular REST path, that TCP is an Unreal fallback, or that the retail client can be served by implementing standard PlayFab endpoints alone.

## Highest-value next evidence

1. Collect an authorized runtime DNS/SNI and socket trace to learn which embedded service families execute and the actual game-server address/transport. Do not attempt TLS interception where certificate controls or authorization prohibit it.
2. Preserve client logs from `%LOCALAPPDATA%` after a normal launch; Unreal logs often expose travel URLs, subsystem selection, request correlation IDs, and failure categories without decrypting traffic.
3. Build a symbol/cross-reference map around the Phoenix functions and domain strings in a disassembler to recover URL construction, verb selection, and serializer call sites. Keep this read-only and avoid anti-cheat tampering.
4. Treat each recovered request/response contract as evidence-backed only after a call site, log, or authorized capture confirms fields and ordering.
