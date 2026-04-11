# Agents

## Start Here

- `README.md`
- `custom_components/unifi_protect_bridge/manifest.json`
- `custom_components/unifi_protect_bridge/config_flow.py`
- `custom_components/unifi_protect_bridge/runtime.py`
- `custom_components/unifi_protect_bridge/webhook.py`
- `docs/project-split.md`

## Notes

- This repository is centered on the Home Assistant custom integration.
- The optional CLI lives in `Hovborg/unifi-protect-bridge-cli`; do not reintroduce CLI package code into this HACS repo.
- HACS installs must work without the CLI.
- Keep Home Assistant compatibility and HACS install flow as the primary concern.
- Prefer official Home Assistant and Ubiquiti sources for behavior and API assumptions.
- Prefer GitHub CLI (`gh`) for GitHub-specific work when it is available and authenticated.
- Use `gh run`, `gh workflow`, `gh pr`, and `gh api` for CI runs, workflow logs, PR state, and GitHub metadata instead of relying on notification emails or manual browser checks.
- Keep using plain `git` for normal local repository operations such as diff, commit, and push.
