# Project Split

UniFi Protect Bridge is split into two GitHub repositories.

## Home Assistant Integration

Repository:

<https://github.com/Hovborg/unifi-protect-bridge>

Purpose:

- HACS custom integration
- Home Assistant config flow
- Home Assistant runtime
- Protect webhook provisioning from inside Home Assistant
- sensors, events, diagnostics, services, and blueprints

Install path:

```text
config/custom_components/unifi_protect_bridge/
```

The CLI is not required for HACS installs. Home Assistant runs this integration
directly and manages UniFi Protect from the config entry.

## CLI

Repository:

<https://github.com/Hovborg/unifi-protect-bridge-cli>

Purpose:

- terminal diagnostics
- UniFi Protect login checks
- camera and automation inspection
- bridge diff/apply support
- Home Assistant setup URL, ping, and resync helpers

The CLI is installed separately with Python tooling and is used manually by an
admin or developer. It is not run by Home Assistant.

## Shared Contract

Both projects must stay aligned on:

- Home Assistant domain: `unifi_protect_bridge`
- Home Assistant resync service: `unifi_protect_bridge.resync`
- Protect automation prefix: `UniFi Protect Bridge:`
- legacy prefix recognition: `HA Protect Bridge:`
- webhook query source naming, such as `source=person`
- supported detection source names

If these values change in the Home Assistant integration, update the CLI repo in
the same work session and release both repositories.
