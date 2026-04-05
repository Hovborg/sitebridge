# HA Protect Bridge

## Goal

Build a Home Assistant custom integration that turns UniFi Protect Alarm Manager webhooks into reliable Home Assistant automation triggers.

## Why not rely only on the built-in Protect integration

The official Home Assistant UniFi Protect integration already provides motion sensors, detected object sensors, thumbnails, clips, and several event entities.

The gap this bridge is trying to close is different:

- direct Alarm Manager webhook ingestion
- a clean automation-first event model
- one place to normalize Protect webhook payloads for person, animal, vehicle, package, motion and related detections
- easier future extension toward cross-system workflows

## Initial event contract

Generic events:

- `ha_protect_bridge_webhook`
- `ha_protect_bridge_detection`

Typed events:

- `ha_protect_bridge_motion`
- `ha_protect_bridge_person`
- `ha_protect_bridge_animal`
- `ha_protect_bridge_vehicle`
- `ha_protect_bridge_package`
- `ha_protect_bridge_line_crossing`
- additional typed events when recognized from payloads

## Example automation shape

```yaml
alias: Protect person detected
triggers:
  - trigger: event
    event_type: ha_protect_bridge_person
actions:
  - action: notify.mobile_app_phone
    data:
      title: Person detected
      message: >-
        {{ trigger.event.data.alarm_name or 'Protect person detection' }}
```

## Important implementation note

The official Ubiquiti webhook article shows a generic JSON example for motion. The broader Protect trigger categories are documented in Alarm Manager docs. That means some payload interpretation for person/animal/package-specific events is still an inference from those official docs plus the structured webhook format.

We should therefore:

- prefer POST webhooks
- log unknown payload shapes safely
- keep normalization rules explicit and testable
