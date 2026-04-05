Læs `/mnt/c/codex_projekts/.ai/infrastructure.md` for delt system-kontekst.
Læs `/mnt/c/codex_projekts/.ai/model-routing.md` for model-valg og token-besparelse.
Læs `/mnt/c/codex_projekts/.ai/conventions.md` for projektstruktur og AI-filkonventioner.

# Sitebridge

## Formål

`Sitebridge` er nu i praksis ved at blive delt op.

Denne repo fokuserer først på en Home Assistant custom integration under `custom_components/ha_protect_bridge`, så den kan blive HACS-installérbar og håndtere UniFi Protect webhooks automatisk.

Shared Python-klienter og CLI bør senere flyttes til en separat pakke/repo, hvis de skal være rene og genbrugelige uden Home Assistant.

## Vigtige Regler

1. HACS-retningen betyder, at al runtime-kode til custom integrationen skal kunne fungere fra `custom_components/ha_protect_bridge/`.
2. Brug officielle eller tydeligt dokumenterede API'er først.
3. Beskriv projektet som uofficielt/community-drevet, medmindre der kommer skriftlig godkendelse fra Ubiquiti.
4. Home Assistant live-adgang på denne Linux-host skal bruge `hass-cli`, aldrig `ha`.
5. Direkte REST-kald til Home Assistant er fallback, hvis MCP og `hass-cli` ikke er nok.
6. Hold hemmeligheder ude af repoet. Brug `.env`, lokale shell-variabler eller secret managers.
7. Hvis en Protect-funktion kun findes via private/ustabile endpoints, skal det markeres eksplicit i docs før implementering.
8. Repoet starter lukket/private-first. Publicering kommer først efter review af navn, docs, sikkerhed og API-scope.

## Scope lige nu

### Inden for scope

- Home Assistant custom integration for Protect Alarm Manager webhooks
- Automatisk oversættelse af webhook-payloads til HA-events
- Understøttelse af motion, person, animal, vehicle, package og beslægtede detection-typer
- Dokumentation for HACS-retning og repo-split

### Uden for scope lige nu

- Fulde UniFi Network/Site Manager klienter i denne repo
- Reverse engineering af private mobil-app endpoints
- Branding der kan forveksles med officiel Ubiquiti software

## Teknisk Retning

- Primær leverance: `custom_components/ha_protect_bridge`
- Dev-værktøjer/tests kan stadig ligge i repo-roden
- Kvalitet: `ruff`, `pytest`, GitHub Actions
- Event-model først, entities senere

## Eventstrategi

Webhooks skal omsættes til:

- et generisk event for alle webhooks
- et generisk detection-event
- et typed event pr. genkendt detection-type, fx `ha_protect_bridge_person`

Det gør automations lette at skrive, også før vi bygger egentlige entities.

## Lokale Kommandoer

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python3 -m compileall custom_components src
```
