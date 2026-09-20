# Login-failure runtime evidence (2026-09-20)

This report covers one normal Epic Games Launcher start of the installed Dauntless client that reached the title screen and displayed **login failed**. No packet payloads were captured. Exchange codes, account identifiers, usernames, local addresses, and unrelated launcher data are omitted.

## Timeline and launch contract

- Epic prepared and launched `start_protected_game.exe` at approximately `15:19:54Z`.
- The protected bootstrapper exited and `Dauntless-Win64-Shipping.exe` became the foreground process at approximately `15:21:31Z`.
- The shipping process exited at approximately `15:22:08Z`, after the login failure.
- The launcher supplied these relevant argument names: `AUTH_LOGIN`, `AUTH_PASSWORD`, `AUTH_TYPE`, `epicapp`, `epicenv`, `EpicPortal`, `epicusername`, `epicuserid`, `epiclocale`, and `epicsandboxid`.
- Observed non-secret values establish `AUTH_TYPE=exchangecode`, `epicapp=Jackal`, `epicenv=Prod`, and `epicsandboxid=jackal`. `AUTH_PASSWORD` carried the short-lived exchange credential and is intentionally not recorded.

This confirms that a normal retail launch begins with an Epic exchange-code login. It does not establish how the code is converted into EOS/Phoenix/Dauntless identity, because HTTPS contents were not inspected.

## Shipping-process socket metadata

The observer sampled 131 socket-state rows for the shipping process. Remote connections were limited to the login/start-screen phase:

| Remote address | Port | Observed states | Ownership clue |
|---|---:|---|---|
| `104.18.124.108` | 443/TCP | SYN sent, established, finish wait | Cloudflare address space |
| `3.233.18.214` | 443/TCP | SYN sent, established | AWS EC2 reverse DNS |
| `34.202.187.14` | 443/TCP | established | AWS EC2 reverse DNS |
| `3.222.97.22` | 443/TCP | established | AWS EC2 reverse DNS |
| `2606:4700:3030::6815:4080` | 80/TCP | SYN sent, established | Cloudflare address space |

No remote UDP flow, matchmaking/game host, beacon port, or Unreal travel connection was observed before failure. The original connection CSV remains ignored under `research/local-captures/` and is not committed.

The first observer version did not retain DNS-cache name mappings, and the relevant cache entries were gone when inspected afterward. Therefore these IPs must not be assigned to specific Phoenix, Epic, EOS, or PlayFab hostnames from this run alone. The observer now records DNS-cache metadata for subsequent launches.

## Local artifacts after failure

- No Archon gameplay `.log` was created. `Saved/Logs/cef3.log` remained unrelated to login.
- `Engine.ini` and `GameUserSettings.ini` were updated, but no endpoint, port, travel URL, or failure code was persisted.
- The pipeline-cache journal and ImGui state changed, confirming normal client initialization without adding protocol evidence.

## Conclusion

The failure occurred before matchmaking and before the Unreal game-server data plane. The evidence narrows the immediate problem to the Epic exchange-code → client identity/backend-login stage. A second normal launch with the enhanced DNS-cache observer can associate the login-stage IPs with hostnames. Exact HTTPS methods, paths, and response/error bodies still require an authorized diagnostic export or deeper call-site analysis; they cannot be inferred from IP ownership.
