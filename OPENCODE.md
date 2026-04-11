# OpenCode

## Start Here

- `README.md`
- `custom_components/unifi_protect_bridge/`
- `custom_components/unifi_protect_bridge/runtime.py`
- `custom_components/unifi_protect_bridge/webhook.py`
- `docs/project-split.md`

## Notes

- The main deliverable in this repository is the Home Assistant integration.
- Do not reintroduce CLI package code into this repository; the optional CLI lives in `Hovborg/unifi-protect-bridge-cli`.
- HACS installs must work without the CLI.
- Keep the HACS install path and runtime behavior simple and explicit.
