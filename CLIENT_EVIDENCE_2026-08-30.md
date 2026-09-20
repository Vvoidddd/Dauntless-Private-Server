# Client Evidence — 2026-08-30

This note records read-only observations from the locally supplied client. It distinguishes file-manifest references from files actually present and treats binary strings as clues, not protocol contracts.

## Manifest observations

`Dauntless/Manifest_UFSFiles_Win64.txt` references:

- `Archon/Archon.uproject`
- `Archon/Plugins/PhoenixMatchmaker/PhoenixMatchmaker.uplugin`
- `Archon/Plugins/PlayFab/PlayFab.uplugin`
- packaged PlayFab-named media and backend assets, including `PlayFabEconomy` assets

`Dauntless/Manifest_DebugFiles_Win64.txt` references `Archon/Binaries/Win64/Dauntless-Win64-Shipping.pdb` and other PDBs. These `.uproject`, plugin descriptor, and shipping PDB paths are manifest entries only: the corresponding loose files inspected were absent. Packaged manifest references do not provide source code or a usable plugin/API specification.

## Binary-string observations

Printable strings in `Dauntless-Win64-Shipping.exe` include:

- `.playfabapi.com` and `.playfabsandbox.com` domain suffixes;
- EOS-related login and error identifiers;
- catalog/inventory and loadout-related identifiers, including `FOnlineLoadoutPhoenix` names;
- Unreal party-beacon/reservation identifiers such as `APartyBeaconClient` and `APartyBeaconHost`.

Together, these observations support the narrow conclusion that the build contains code or data referring to PlayFab-style domains, EOS identity/error concepts, Phoenix online features, loadouts/catalogs, and Unreal party beacons. They do not establish which paths execute, exact endpoint URLs, request/response bodies, authentication flows, server ports, encryption, deployment configuration, or compatibility requirements.

## Limits and safety boundary

- No live traffic capture, service login, credential/token collection, or server interaction was used for this note.
- No credentials, title keys, product secrets, or private endpoints are recorded.
- String presence does not prove active runtime use and may include engine, fallback, debug, or unused code.
- Manifest presence does not mean a referenced loose file was shipped.
- This evidence does not demonstrate retail-client compatibility with this repository.
- This project does not provide DLL injection, Epic impersonation, DRM circumvention, or Easy Anti-Cheat bypass. Any future EOS work must use an authorized developer integration with owned credentials and applicable terms review.
