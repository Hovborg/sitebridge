# Architecture

## New direction

The repository is now split conceptually into two future deliverables:

- a Home Assistant custom integration for Protect webhook bridging
- a later shared Python library / CLI split

For now, this repo prioritizes the Home Assistant side because HACS has stricter packaging expectations than a generic CLI project.

## Runtime layers in this repo

### 1. Home Assistant custom integration

`custom_components/ha_protect_bridge/`

Responsibilities:

- create and manage the webhook endpoint
- receive Protect Alarm Manager webhooks
- normalize payloads
- fire HA events that automations can consume

### 2. Dev helper code

`src/sitebridge/`

This is no longer the primary product surface. It can remain as helper code while the HACS integration takes shape, but shared CLI/core logic should eventually move out to its own package or repository.

## Event-first approach

The first implementation target is events, not entities.

Why:

- person/animal/vehicle/package automations become useful immediately
- event payloads are easier to normalize than dynamic entities
- it matches Protect Alarm Manager and webhook-driven flows naturally

## Planned next layers

1. typed HA events from webhook payloads
2. options/config for filters and noise reduction
3. optional entities for "last event", counters, and convenience sensors
4. separate shared client library / CLI
