# PlayFab configuration guide

This guide describes a safe setup for a PlayFab title owned and administered by the project owner. It deliberately contains placeholders and no working credentials. Do not configure this project against a title, tenant, game, or platform account you do not own or have explicit authorization to administer.

## Before configuring the application

1. Create separate PlayFab titles for local/development and production use in Game Manager.
2. Record each title's Title ID and API endpoint from the owner's PlayFab configuration.
3. Select only supported authentication methods that the owner can legitimately operate. Do not imitate Epic, EOS, Phoenix Labs, or retail Dauntless identity.
4. Create a minimal Economy V2 catalog in the development title before enabling inventory writes.
5. Configure Statistics/Leaderboard definitions only after their authoritative writers and privacy implications are documented.
6. If custom server logic is required, register owner-controlled Azure Functions with PlayFab CloudScript. Microsoft recommends the Azure Functions path for newer CloudScript workflows: <https://learn.microsoft.com/en-us/gaming/playfab/live-service-management/service-gateway/automation/cloudscript/>.

The current application consumes the identity-link variables shown below. Economy, CloudScript, multiplayer hosting, and alternative data backends remain design guidance rather than implemented adapters.

## Proposed environment variables

Place local values in an ignored `.env` file or, preferably for deployed environments, inject them from a managed secret store. Commit only a `.env.example` containing placeholders.

```dotenv
# Public/non-secret PlayFab routing value.
DPS_PLAYFAB_TITLE_ID=YOUR_DEVELOPMENT_TITLE_ID

# Secret server credential. Never use this from a client, launcher, browser,
# packaged game, log message, exception response, test fixture, or repository.
DPS_PLAYFAB_SECRET_KEY=LOAD_FROM_SECRET_STORE

# Implemented finite request timeout (0.5 to 30 seconds).
DPS_PLAYFAB_TIMEOUT_SECONDS=5
```

The API host must be derived from or checked against the configured Title ID to prevent credential forwarding to an attacker-controlled origin. Production should use an allow-listed HTTPS hostname and normal certificate validation. Do not expose configuration endpoints that echo secrets.

## Secret handling

- Treat the PlayFab title secret key as a high-privilege server credential. Store it in Azure Key Vault, the deployment platform's secret manager, or a protected environment-variable facility.
- Never prefix a secret with a client-build convention or ship it in Unreal configuration, JavaScript, desktop binaries, mobile packages, source maps, or launcher settings.
- Give CI separate development credentials and restrict who can read deployment secrets. Use protected environments for production.
- Keep development and production titles, catalogs, Azure subscriptions, function registrations, and secrets separate.
- Rotate a credential immediately if it enters Git history, logs, screenshots, chat, crash reports, or build artifacts. Removing the latest file is not sufficient after a commit.
- Redact authentication headers, entity/session tickets, secret keys, function keys, email addresses, and request bodies containing player data from logs.
- Do not use an `X-SecretKey` from any player-controlled process. The server-side CloudScript API documents that this header is the title secret: <https://learn.microsoft.com/en-us/rest/api/playfab/server/server-side-cloud-script/execute-cloud-script?view=playfab-rest>.
- Prefer short-lived player session/entity tokens for player-context calls and service-held credentials only for trusted backend operations.

## Identity configuration

The future login adapter should validate a PlayFab-issued session ticket or entity token, obtain the caller's EntityKey, and map it to the local account record. It must not accept `playfab_id`, `entity_id`, `character_id`, or an email address as authentication by itself.

Maintain these invariants:

- One verified title-player entity maps to one local account unless an explicit account-linking workflow says otherwise.
- Character ownership is checked through the authenticated entity relationship on every operation.
- Account linking is a sensitive, re-authenticated operation with an audit event and conflict handling.
- Authentication errors returned to clients do not reveal whether a third-party account or email exists.
- Administrative APIs and title-secret operations are unavailable on public client routes.

PlayFab's Entity API uses entity tokens for entity-scoped operations; for example, the CloudScript Execute Function endpoint requires `X-EntityToken`: <https://learn.microsoft.com/en-us/rest/api/playfab/cloudscript/server-side-cloud-script/execute-function?view=playfab-rest>.

## Economy configuration

In the development title:

1. Create Catalog V2 items with stable IDs for the smallest test set, such as one material and one non-stackable equipment item.
2. Create virtual currencies only for fungible balances used in purchase/exchange flows.
3. Publish the catalog. Keep draft and published content workflows distinct.
4. Choose collection IDs for account-wide and character-specific goods. Persist the mapping; do not infer ownership from a client-supplied collection name.
5. Define all reward tables in server-owned configuration with an explicit version and catalog validation.
6. Test `GetInventoryItems`, idempotent grants, ETag conflicts, atomic batch failure, continuation tokens, and throttling before adding more content.

Catalog and inventory concepts are documented at <https://learn.microsoft.com/en-us/gaming/playfab/economy-monetization/economy-v2/catalog/catalog-overview> and <https://learn.microsoft.com/en-us/xbox/playfab/economy-monetization/economy-v2/inventory/>. Economy limits must be incorporated into the retry, cache, pagination, and batching design: <https://learn.microsoft.com/en-us/gaming/playfab/economy-monetization/economy-v2/limits>.

Client routes may request a purchase, crafting recipe, or completed-action processing, but they must not pass arbitrary authoritative item IDs, currency amounts, XP values, prices, or grant quantities. Resolve those values from published catalog data and versioned server rules.

## Progression and leaderboard configuration

Create only the definitions required for a documented game feature. For every statistic record:

- definition name and environment;
- entity type;
- columns and aggregation behavior;
- authoritative writer;
- reset/version schedule;
- corresponding leaderboard, if any;
- retention and reconciliation behavior;
- client visibility and abuse impact.

Do not enable arbitrary client statistic posting for competitive measures. Microsoft warns that doing so lets players post arbitrary scores: <https://learn.microsoft.com/en-us/gaming/playfab/community/leaderboards/tournaments-leaderboards/using-player-statistics>.

Private quest/progression documents should include a schema version and reward-configuration version. Migrations must be idempotent, observable, and reversible where practical.

## CloudScript and authoritative servers

Use Azure Functions CloudScript for low-frequency trusted operations such as daily claims, receipt/reward validation, and administrative reconciliation. Functions must validate identity, authorization, input shape, replay state, and the server-owned reward definition. Treat each invocation as stateless; never depend on one player reaching the same function instance twice.

Use an authoritative multiplayer server for live hunts. It should receive an allocation/session identity, authenticate each joining player, own combat and outcome state, and submit one completion record. PlayFab durable services should not receive high-frequency movement or combat writes. Microsoft's backend consumption guidance explains this division: <https://learn.microsoft.com/en-us/xbox/playfab/pricing/consumption-best-practices>.

## Network and retry policy

- Set finite connect/read timeouts on every PlayFab request.
- Retry only operations whose semantics are known. Use the identical stable `IdempotencyId` for an identical transactional retry.
- For ETag conflicts, re-read and recompute rather than resending a stale write.
- Use exponential backoff with jitter for transient failures and throttling; cap attempts and move unresolved work to a durable retry/dead-letter state.
- Do not turn a timeout into a second logical operation ID.
- Propagate an internal correlation ID through logs and PlayFab `CustomTags`, but never put credentials or personal data in tags.
- Restrict outbound PlayFab calls to the configured HTTPS endpoint and validate certificates normally.

Official idempotency and concurrency guidance: <https://learn.microsoft.com/en-us/gaming/playfab/economy-monetization/economy-v2/tutorials/idempotent-transactions-and-retries> and <https://learn.microsoft.com/en-us/xbox/playfab/economy-monetization/economy-v2/tutorials/etags-and-concurrency-control>.

## Local, CI, and production profiles

### Local default

Keep `DPS_DATA_BACKEND=sqlite`. No PlayFab secrets are needed. Unit tests must not contact PlayFab. Adapter contract tests should use deterministic fakes.

### Development integration

Use a development PlayFab title with test users, a minimal catalog, low-value fake currency, and non-production Azure Functions. Integration tests must be explicitly enabled and should clean up only records they created. Avoid running them automatically on every local test invocation.

### CI

Run unit/contract tests without credentials on ordinary pull requests. Run PlayFab integration tests only in a protected workflow against the development title. Mask secrets and prevent untrusted fork workflows from receiving them.

### Production

Require protected deployment approval, retrieve secrets at runtime, disable debug mode, use HTTPS at the external edge, apply least-privilege network access, and enable security/audit monitoring. Production migrations and catalog publishing require an explicit rollback or forward-fix procedure.

## Verification checklist

- `.env`, `.venv`, `.vs`, caches, local databases, logs, and the local `dauntless` game folder are ignored by Git.
- Repository history and build artifacts contain no title secret, function key, connection string, ticket, or real player data.
- Development and production Title IDs and secrets are distinct.
- The configured API host matches the configured Title ID and uses HTTPS.
- Public routes never use caller-supplied entity IDs as authorization.
- Every inventory mutation has a stable operation ID and canonical request hash.
- Conflicting replays, throttling, timeouts, ETag conflicts, and partial cross-service failures have automated tests.
- Catalog and statistic IDs are validated at startup or deployment, not first discovered during a live reward.
- Operational dashboards cover request failures, throttling, duplicate/conflicting operations, reward anomalies, and reconciliation drift.
- Backup, rotation, incident-response, and reconciliation procedures have been exercised.

## Non-goals

This configuration does not connect to or impersonate the original Dauntless PlayFab/Epic environment. It does not disable EAC, forge EOS authentication, bypass platform entitlements, patch the retail client, or supply Unreal replication/gameplay hosting. Any working integration must use an owner-controlled title, owner-controlled client/server software, official authentication, and authorized platform services.
