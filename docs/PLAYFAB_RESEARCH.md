# PlayFab integration research

This document records an architecture direction, not a claim that the current HTTP service is compatible with the retail Dauntless client. The recommendations use only Microsoft PlayFab documentation and assume a PlayFab title controlled by this project's owner.

## Recommended service boundary

Keep FastAPI as the backend-for-frontend and orchestration layer. Put PlayFab behind a narrow adapter so local development can continue using SQLite while deployed environments use PlayFab APIs. Do not make the SQLite schema or public REST responses imitate undocumented game protocols.

PlayFab should hold durable identity-linked data, catalog content, inventory, progression statistics, and leaderboard state. Party membership, matchmaking tickets, and live hunt state are ephemeral orchestration data. Real-time simulation belongs on an authoritative game server, not in Entity Objects, Title Data, or per-action CloudScript calls. Microsoft's consumption guidance recommends loading durable state when a session starts, maintaining live state on the game server, and persisting at the end of a session or periodically during long sessions: <https://learn.microsoft.com/en-us/xbox/playfab/pricing/consumption-best-practices>.

## Identity and entities

PlayFab's entity model distinguishes title player accounts, master player accounts, characters, groups, titles, and game servers. Player Data is scoped to `title_player_account`, `master_player_account`, and `character`; Microsoft recommends Entity Objects for new titles: <https://learn.microsoft.com/en-us/gaming/playfab/player-progression/player-data/>.

Use the authenticated PlayFab `title_player_account` EntityKey as the durable external identity. A local account ID can remain an internal foreign key, but it must have an explicit one-to-one mapping to the PlayFab entity ID and type. Never accept an entity ID from a request and treat it as proof of ownership; derive the caller from a validated ticket/entity token and authorize the requested target.

Represent each game character with a PlayFab `character` EntityKey. Small profile or progression documents may be Entity Objects, which are JSON-serializable objects attached to an entity: <https://learn.microsoft.com/en-us/xbox/playfab/live-service-management/game-configuration/entities/entity-objects>. Files are better for larger save payloads, but should not become a high-frequency mutable database: <https://learn.microsoft.com/en-us/gaming/playfab/live-service-management/game-configuration/entities/entity-files>.

Title Data is appropriate for global, slowly changing configuration such as feature flags or balance-table version pointers. It is cached and changes can take up to 15 minutes to propagate, so it is not suitable for locks, counters, hunt state, or other mutable global variables: <https://learn.microsoft.com/en-us/gaming/playfab/live-service-management/game-configuration/titledata/>.

## Economy V2, catalog, currencies, and inventory

Use Economy V2. Microsoft describes Economy V1 as bug-fix-only and recommends V2 for new development: <https://learn.microsoft.com/en-us/xbox/playfab/economy-monetization/economy-v2/overview>.

Every grantable item must refer to a published Catalog V2 item ID. The catalog is the source of truth for items, virtual currencies, bundles, stores, subscriptions, localized descriptions, prices, tags, and content metadata: <https://learn.microsoft.com/en-us/gaming/playfab/economy-monetization/economy-v2/catalog/catalog-overview>. A fungible token used for purchases should normally be modeled as a virtual currency; an owned material, weapon, cell, cosmetic, or consumable should be a catalog item.

Economy V2 inventories support collections, unique and non-unique items, multiple stacks of one item, stack amounts, and display properties: <https://learn.microsoft.com/en-us/xbox/playfab/economy-monetization/economy-v2/inventory/>. A collection per character is a reasonable mapping if inventory truly belongs to a character. Account-wide goods should remain in a player-level collection. Do not encode all inventory as `(character_id, item_code, quantity)` because that cannot represent distinct instances, multiple stacks, stack metadata, expiration, or catalog-backed currencies.

Use `ExecuteInventoryOperations` for atomic multi-item grants, crafting, and exchanges. Operations execute sequentially and the entire batch succeeds or fails together: <https://learn.microsoft.com/en-us/rest/api/playfab/economy/inventory/execute-inventory-operations?view=playfab-rest>.

Economy V2 does not natively replace every legacy feature. Player-to-player trading, finite global supply, randomized drop tables, and some time-based recharge mechanics require trusted custom orchestration, commonly Azure Functions: <https://learn.microsoft.com/en-us/xbox/playfab/economy-monetization/economy-v2/overview>.

## Progression, statistics, and leaderboards

Separate private progression state from public/rankable measurements.

- Store structured quest state, unlock flags, mastery branches, loadouts, and the version of the progression curve in a character Entity Object or another owner-controlled durable store.
- Keep balance curves and reward definitions server-controlled and versioned. A client may request an action but must not choose its XP, item grants, or resulting level.
- Use Statistics V2 for numeric measures that require aggregation, querying, or leaderboard linkage, such as total hunts, fastest completion time, seasonal score, or trials rank.
- Use Leaderboards V2 for rank views and seasonal versions. Do not create one leaderboard definition per quest or character.

Legacy player-statistics documentation warns that statistics are readable and that enabling client writes lets players post arbitrary scores; competitive statistics should never be client-authored: <https://learn.microsoft.com/en-us/gaming/playfab/community/leaderboards/tournaments-leaderboards/using-player-statistics>. The current Leaderboards quickstart is under the Progression service: <https://learn.microsoft.com/en-us/gaming/playfab/features/new-leaderboards-statistics/leaderboards/quickstart-leaderboards>.

`level` should be derived deterministically from authoritative XP and a versioned curve unless there is a strong reason to persist both. If both are persisted, update them transactionally in the owner-controlled service and define a repair process for divergence.

## Idempotency, ETags, and concurrency

Network retries are normal. Every logical purchase, reward, transfer, and crafting request needs one stable operation ID generated before the first attempt. Economy V2 accepts `IdempotencyId` on inventory writes, retains it for 14 days, returns the original result for an identical retry, and rejects reuse with different request data. Microsoft specifically recommends a deterministic quest/player-style ID for server reward grants: <https://learn.microsoft.com/en-us/gaming/playfab/economy-monetization/economy-v2/tutorials/idempotent-transactions-and-retries>.

ETags solve a different problem: optimistic concurrency for read-modify-write operations. Read the inventory, retain its ETag, and send that value with the conditional write. On conflict, re-read, re-evaluate, and issue a new operation. Microsoft advises against combining ETag and `IdempotencyId` in the same retry flow because identical-retry and re-read/recompute semantics conflict: <https://learn.microsoft.com/en-us/xbox/playfab/economy-monetization/economy-v2/tutorials/etags-and-concurrency-control>.

Serialize writes targeting one entity where practical. PlayFab notes that concurrent reads are generally safe, while concurrent writes to one player, character, or group can return `APIConcurrentRequestLimitExceeded` or `ConcurrentEditError`: <https://learn.microsoft.com/en-us/gaming/playfab/api-references/>.

Maintain a durable application-side operation ledger or outbox for workflows spanning Economy and Statistics. Record the operation ID, player/character, hunt ID, build and reward-table version, canonical request hash, state, attempts, and response identifiers. A duplicate ID with a different hash is a conflict, not a new reward.

## Important service limits

The limits below are design constraints, not capacity targets. Recheck the official limits before launch because Microsoft can revise them.

Economy V2 currently documents, among other constraints, 40 inventory reads per 60 seconds per player/API, 20 inventory writes per 60 seconds per player/API, 10,000 items per inventory collection, 50 operations and 300 modified items per batch, and inventory page sizes of 50 uncompressed or 250 compressed. Catalog pages have a maximum of 50 items; catalog display properties are limited to 10,000 bytes and inventory-item display properties to 1,000 bytes. See the full and authoritative table: <https://learn.microsoft.com/en-us/gaming/playfab/economy-monetization/economy-v2/limits>.

Statistics documents a default/update budget of 30 requests per 120 seconds for relevant operations, plus development/live definition quotas and a maximum of five columns: <https://learn.microsoft.com/en-us/gaming/playfab/player-progression/statistics/limits-statistics> and <https://learn.microsoft.com/en-us/gaming/playfab/player-progression/statistics/quota-statistics>.

Leaderboards documents 50 definitions, 10,000 rows, and one version in development mode; live mode documents 1,000 definitions, one million rows, and unlimited versions, with at most five columns: <https://learn.microsoft.com/en-us/gaming/playfab/community/leaderboards/quota-leaderboards>.

Consequences:

- Cache catalog/configuration data and use continuation tokens.
- Batch inventory changes; never write inventory for every animation, pickup tick, or frame.
- Coalesce statistic updates at authoritative session boundaries.
- Back off with jitter on throttling and honor service retry information.
- Monitor quota use in Game Manager and load-test with realistic per-player access patterns.

## Authoritative reward flow

The recommended completed-hunt flow is:

1. An allocated, trusted game server owns the hunt simulation and produces a completion record. A retail client or party leader cannot self-attest completion.
2. The backend validates the server identity, build compatibility, roster, hunt assignment, outcome, duration bounds, and replay status.
3. The backend selects rewards from a server-controlled, versioned reward table. The request never accepts arbitrary item IDs, quantities, currency, or XP from the client.
4. It derives a stable operation ID such as `hunt:{hunt-id}:character:{entity-id}:rewards:{version}` and records a canonical request hash in the operation ledger.
5. It applies the catalog-backed item and currency changes atomically with `ExecuteInventoryOperations` and the stable idempotency ID.
6. It updates private progression and Statistics V2 using service credentials, with a durable outbox if those operations cannot be one transaction.
7. It marks the operation complete and returns the recorded result. An identical replay returns that result; a changed replay is rejected and audited.

CloudScript can expose trusted server logic and prevent clients from tampering with daily rewards or similar operations: <https://learn.microsoft.com/en-us/gaming/playfab/live-service-management/service-gateway/automation/cloudscript/>. Prefer CloudScript using Azure Functions for new custom functions. It remains stateless compute, not the real-time simulation host.

## Local-to-PlayFab model mapping

| Current local model | PlayFab direction | Required change |
| --- | --- | --- |
| `accounts.id` | `title_player_account` EntityKey mapping | Add explicit external entity ID/type; validate PlayFab authentication rather than trusting supplied IDs. |
| `gameplay_characters` | `character` entity plus a small profile/progression object | Replace or map integer IDs; version structured progression; derive level from XP where possible. |
| `gameplay_inventory` | Economy V2 collection, catalog item ID, stack ID, amount, properties | Redesign. The current composite key cannot represent unique instances, multiple stacks, metadata, expiration, or currencies. |
| `training-token` literal | Published catalog item or virtual currency | Remove free-form authoritative item codes; validate all references against a catalog/reward definition. |
| `gameplay_parties` | Ephemeral party/orchestration state | Keep out of durable player data; add expiry, reconnect, and distributed ownership if deployed. |
| `gameplay_matchmaking` | PlayFab Multiplayer ticket/queue state or local adapter | Redesign state transitions around external ticket IDs and asynchronous allocation. |
| `gameplay_hunt_results` | Reward-operation ledger and audit record | Preserve the idempotency concept but scope the key, bind it to a canonical hash and trusted server, and retain reward/build versions. |
| `experience` and `level` | Private progression object; selected rankable metrics in Statistics V2 | Define one authoritative source, a versioned curve, transaction/outbox behavior, and reconciliation. |

## Phased implementation

### Phase 0: boundaries and interfaces

Define `IdentityProvider`, `PlayerDataStore`, `EconomyProvider`, `ProgressionProvider`, and `RewardLedger` interfaces. Preserve SQLite implementations for tests. Define typed EntityKey, CatalogItemReference, inventory stack, currency amount, and operation-result models.

### Phase 1: identity and read-only integration

Create an owner-controlled PlayFab development title, register allowed login methods, validate login/session tokens, map local accounts to title-player entities, and add health diagnostics that reveal no credentials. Read catalog and player inventory through the adapter with pagination and throttling tests.

### Phase 2: catalog and inventory writes

Create a minimal versioned development catalog, currencies, and explicit reward definitions. Add idempotent server-only inventory grants and atomic crafting/exchange operations. Introduce ETag-specific read-modify-write tests, rate-limit backoff, an audit ledger, and reconciliation tooling.

### Phase 3: progression and rankings

Move structured progression to versioned objects, define the XP curve and migration strategy, then create the small set of Statistics/Leaderboard definitions actually required. All competitive writes remain server-authoritative.

### Phase 4: authoritative sessions

Integrate matchmaking/allocation with a clean-room, authorized game-server build. The game server loads durable state, owns live state, signs completion reports, and flushes rewards/progression at controlled boundaries. Test retries, duplicated reports, partial downstream failures, reconnects, and stale builds.

### Phase 5: operations

Add dashboards for throttling, failures, duplicate/conflicting operation IDs, Economy transaction history, reward anomalies, and reconciliation drift. Separate development and production titles and secrets, use staged catalog publishing, document rollback, and run restore/reconciliation exercises.

## Exact limitations

- PlayFab supplies backend primitives; it does not make this Python API a native Unreal gameplay server.
- These services do not provide Unreal actor replication, movement, combat, behemoth AI, map hosting, or retail-client protocol compatibility.
- An owner-controlled PlayFab title and credentials cannot impersonate Epic, Phoenix Labs, or an existing production title.
- This design does not bypass EAC, EOS, platform authentication, entitlement checks, certificate pinning, or client integrity controls.
- A Title ID alone is not enough. The owner must configure authentication, catalog content, permissions, queues/builds where applicable, Azure Functions, secrets, quotas, and billing.
- Entity Objects and Title Data are not high-frequency transactional stores. Economy, Statistics, and Leaderboards are rate-limited and may be eventually consistent across workflows.
- Economy idempotency lasts 14 days; permanent replay protection for immutable hunt IDs therefore still requires the project's durable operation ledger.
- Cross-service Economy/progression/statistics writes are not one global transaction. Use an outbox, retry state machine, audit trail, and reconciliation.
- Economy V2 lacks native equivalents for some legacy systems, including direct player trading and drop-table behavior; trusted custom orchestration is required.
- Official service behavior and limits can change. Revalidate documentation, SDK/API versions, title limits, pricing, and platform policy before any deployment.
