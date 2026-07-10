# Config-flow URL serialization fix

## Goal

Restore the UniFi Protect Bridge config form on Home Assistant 2026.7 while
preserving the integration's existing webhook base URL normalization and
origin-only validation.

## Root cause

`_build_full_schema()` embeds `_validate_webhook_base_url` as a Voluptuous
validator. Home Assistant serializes config-flow schemas before sending them to
the frontend. Its serializer cannot convert arbitrary Python validator
functions, so opening the flow raises `ValueError` and returns HTTP 500.

## Design

The form schema will expose `webhook_base_url` as `str`, which Home Assistant
can serialize. Strict validation will remain in `_validate_webhook_base_url`,
but it will run after form submission instead of during schema serialization.

Both the initial user flow and reconfigure flow will catch an invalid webhook
base URL and return the same form with the existing `webhook_base_url` error
translation. Invalid URL input must not attempt a Protect connection and must
not escape as an HTTP 500.

Valid values retain the current behavior:

- surrounding whitespace is removed;
- an optional trailing slash is removed;
- only absolute `http` and `https` origins are accepted;
- the origin must contain a hostname and a valid numeric port when a port is
  present;
- URL-embedded usernames and passwords are rejected;
- paths, queries, fragments, and embedded webhook tokens are rejected;
- a blank override is omitted from new entries and clears an existing override
  during reconfiguration.

No runtime, webhook, Protect automation, credential, or CLI behavior changes.

## Tests

Add regression coverage that:

1. serializes the complete form schema using the same
   `voluptuous_serialize.convert()` path used by Home Assistant;
2. confirms invalid URL input returns a form error without calling Protect;
3. covers both initial setup and reconfiguration;
4. preserves the existing normalization and rejection cases.

Verification consists of the focused config-flow tests, the full pytest suite,
Ruff, and schema/API smoke tests against both the declared minimum Home
Assistant version and the current Home Assistant release. The serialization
smoke must run in CI so a future Home Assistant schema change cannot be hidden
by the repository's lightweight unit-test stubs.

## Publication

Implement the fix on `fix/config-flow-url-serialization`. Do not merge PR #2 as
written because it weakens existing validation and can raise another exception
for a non-empty override. After local verification, review the diff and ask for
explicit approval before pushing, merging, commenting, or closing GitHub items.
