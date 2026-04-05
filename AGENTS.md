Læs `AI_CONTEXT.md` for projektbeskrivelse og regler.
Læs `/mnt/c/codex_projekts/.ai/infrastructure.md` for delt system-kontekst.

# Codex/OpenAI - Sitebridge

## Første Filer

- `AI_CONTEXT.md`
- `README.md`
- `custom_components/ha_protect_bridge/manifest.json`
- `custom_components/ha_protect_bridge/normalize.py`
- `docs/repo-split.md`

## Noter

- Hovedleverancen i denne repo er nu HA custom integrationen.
- HACS-reglerne betyder, at integrationens runtime-kode skal fungere fra `custom_components/ha_protect_bridge/`.
- Shared library/CLI er et senere split, ikke første leverance her.
