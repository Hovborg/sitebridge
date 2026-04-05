# APIs And Scope

Status reviewed against official sources on **5 April 2026**.

## Key finding: this should be split

The official sources point toward a split architecture:

- HACS expects one integration per repository under `custom_components/`
- Ubiquiti splits official surfaces into Site Manager, local app APIs, Protect, and Access
- Home Assistant treats UniFi Network and UniFi Protect as separate integrations

## What this repo should cover first

This repo should cover the Home Assistant bridge for UniFi Protect webhooks first.

Specifically:

- Protect Alarm Manager webhook ingestion
- normalized HA events for motion, person, animal, vehicle, package, and related triggers
- a HACS-friendly custom integration structure

## What should move elsewhere later

These should become a separate shared package/repository later:

- Site Manager client
- UniFi Network client
- generic CLI for non-HA users
- wider multi-product bridge logic

## Home Assistant

- Use `hass-cli` on this Linux host for live operational checks.
- Use HA custom integration structure for runtime code.

## UniFi Protect

Officially relevant capabilities for this bridge:

- Alarm Manager supports Protect triggers for person, vehicle, package, animal, motion, sound, line crossing, NFC, doorbell and more.
- Webhook actions can send GET or POST to a custom URL.
- POST should be preferred for richer structured payloads.

## Naming rule

The repository/package naming can change later, but runtime domain naming should stay neutral and unofficial.
