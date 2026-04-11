# Claude Code

## Start Here

- `README.md`
- `custom_components/unifi_protect_bridge/manifest.json`
- `custom_components/unifi_protect_bridge/config_flow.py`
- `custom_components/unifi_protect_bridge/runtime.py`
- `custom_components/unifi_protect_bridge/webhook.py`
- `docs/project-split.md`

## Notes

- This repository is primarily a Home Assistant custom integration.
- The optional CLI lives in `Hovborg/unifi-protect-bridge-cli`; do not add CLI package code here.
- HACS installs must work without the CLI.
- Treat UniFi Protect automation payload assumptions carefully and document inference when needed.
- Prefer official Home Assistant and Ubiquiti sources for product behavior.
