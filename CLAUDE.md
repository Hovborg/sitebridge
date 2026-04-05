Læs `AI_CONTEXT.md` for projektbeskrivelse og regler.
Læs `/mnt/c/codex_projekts/.ai/infrastructure.md` for delt system-kontekst.
Læs `/mnt/c/codex_projekts/.ai/model-routing.md` for model-valg og token-besparelse.

# Claude Code - Sitebridge

## Første Filer

- `AI_CONTEXT.md`
- `README.md`
- `custom_components/ha_protect_bridge/manifest.json`
- `custom_components/ha_protect_bridge/webhook.py`
- `docs/repo-split.md`

## Claude-Specifikke Noter

- Denne repo er nu først og fremmest HA Protect bridge / HACS-retning.
- Brug officielle Home Assistant- og Ubiquiti-kilder ved arkitekturvalg.
- Brug `hass-cli` for live Home Assistant checks på denne host.
- Vær skeptisk over for antagelser om Protect payloads; dokumentér hvad der er inferens.
