# Local Dauntless runtime evidence (2026-09-20)

## Scope and handling

This is a read-only review of locally retained Dauntless/Archon runtime artifacts, launcher metadata, crash locations, and the Windows hosts file. Authentication values, cookies, account identifiers, email addresses, and unrelated launcher-user data are intentionally omitted. No game process was started and no network traffic was intercepted.

## Sources inspected

| Source | Last modified (local time) | Result |
|---|---:|---|
| `C:\Users\tolik\AppData\Local\Archon\Saved\Config\WindowsClient\Engine.ini` | `2024-12-16T15:54:04.8723307-05:00` | Contains a persisted `GameNetDriver StatelessConnectHandlerComponent` client ID setting. |
| `C:\Users\tolik\AppData\Local\Archon\Saved\Config\WindowsClient\GameUserSettings.ini` | `2026-09-15T12:14:15.4542527-04:00` | Contains Archon client preferences including `bIsLanMatch=True`, blank `LastRegion`, cross-play disabled, and Epic-friends chat filtering. |
| `C:\Users\tolik\AppData\Local\Archon\Saved\Logs\cef3.log` | `2024-12-16T13:52:23.6829824-05:00` | Only a CEF GPU initialization warning; no service or network evidence. |
| `C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\AEAFC1CB1043A5299993AA2AEEF95BE1.item` | `2026-09-15T12:44:29.4293398-04:00` | Identifies the installed Epic application and launcher behavior. Sensitive/nonessential manifest values were not copied. |
| `C:\Users\tolik\AppData\Local\EpicGamesLauncher\Saved\Logs\EpicGamesLauncher-backup-2026.09.15-16.44.05.log` | `2026-09-15T12:44:05-04:00` | Confirms the installed `jackal` product/version; the sampled session launched another title, not Dauntless. |
| `C:\Users\tolik\AppData\Local\EpicGamesLauncher\Saved\Logs\EpicGamesLauncher-backup-2026.09.16-04.58.23.log` | `2026-09-16T00:58:23-04:00` | Confirms the installed `jackal` product/version; no Dauntless launch sequence was retained. |
| `C:\Users\tolik\AppData\Local\EpicGamesLauncher\Saved\Logs\EpicGamesLauncher.log` | `2026-09-18T11:49:05.7849040-04:00` | Confirms the installed `jackal` product/version; no Dauntless launch sequence was retained. |
| `C:\WINDOWS\System32\drivers\etc\hosts` | `2025-12-01T17:50:36.7760262-05:00` | No entries containing Epic, EOS, Dauntless, Phoenix, PlayFab, or Jackal. |
| `C:\Users\tolik\OneDrive\Desktop\Dauntless Private Server\Dauntless` | game files dated principally `2026-08-16` | No `.log`, `.dmp`, runtime `.ini`, or crash report was present in the game directory. Only distribution manifests, EAC settings/licenses, and CEF licensing text matched the artifact scan. |

The following expected locations were also searched: `%LOCALAPPDATA%\CrashDumps`, `%LOCALAPPDATA%\Microsoft\Windows\WER`, `%PROGRAMDATA%\Microsoft\Windows\WER`, the Archon `Saved` tree, and Epic launcher `Saved\Crashes`. No Dauntless/Archon gameplay crash report or minidump was found. Epic launcher crash archives exist, but they describe launcher/EOS installer failures rather than an Archon game session and therefore do not establish the game protocol.

## Established findings

### Epic product and launch boundary

The Epic item manifest identifies:

- catalog namespace: `jackal`
- application name: `Jackal`
- display name: `Dauntless`
- application version: `2.1.1.682875`
- launch executable: `start_protected_game.exe`
- `bRequiresAuth=True`
- `bCanRunOffline=True`
- `bAllowUriCmdArgs=False`

The two boolean flags are launcher metadata, not proof that the game can enter its online gameplay flow without authentication. The protected launcher is the configured entry point. No retained launcher log contains an actual Dauntless launch command line, so no Dauntless authentication argument names or values are established here.

### Unreal networking configuration

`Engine.ini` contains a section named `[GameNetDriver StatelessConnectHandlerComponent]` with a persisted cached client identifier. This is evidence that the client uses Unreal's `GameNetDriver` stateless connection handler. The numeric cached value is local state and is deliberately not reproduced because it adds no protocol value.

This setting does **not** establish:

- the concrete `NetDriver` class,
- an IP address or DNS name,
- a UDP/TCP port,
- network/game protocol versions,
- encryption or packet-handler configuration,
- beacon classes or reservation flow,
- control-channel messages,
- gameplay RPCs or replicated classes.

### LAN and online-service preferences

`GameUserSettings.ini` contains `bIsLanMatch=True`, an empty `LastRegion`, cross-play disabled, and an Epic-friends-only chat preference. The LAN flag is a saved user setting, not proof that this retail build exposes LAN matchmaking or will accept a direct local server. It should be treated as a useful experiment variable for a future authorized launch, not a conclusion about transport or admission.

### DNS/host overrides

The Windows hosts file has no relevant override. Therefore, no local DNS redirection for Dauntless/Phoenix/Epic/EOS/PlayFab is evidenced. This says nothing about normal DNS answers, encrypted DNS, cached answers, or destinations selected dynamically at runtime.

## Requested fields for which no local evidence exists

The retained artifacts do not contain matchmaking operation names, HTTP routes, server/travel URLs, destination hosts, map names, game modes, ports, beacon events, build/network compatibility values, control-channel failures, RPC names, or replication traces. Assigning values to any of those fields from this scan would be speculation.

In particular, neither the common Unreal default port nor any previously guessed endpoint should be promoted into the implementation based on these files.

## Evidence gap and next capture

The useful next input is a normal, authorized, version-matched Dauntless launch that retains the Archon log from process start through matchmaking and travel. Before launching, preserve the current `Saved\Logs` state; afterward, copy the newly created Archon log before another launch rotates it. If normal logging is suppressed by the shipping build, an OS-level packet metadata capture can still establish DNS names, remote IPs, transport, ports, and timing, while an authorized HTTP debugging export may establish service routes if certificate pinning does not prevent it.

Any capture shared with the repository must pass through the existing redaction/analyzer workflow. Raw launch command lines and raw headers must not be committed because Epic launcher command lines can contain short-lived credentials.
