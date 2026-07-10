# v0.2.22 config-flow compatibility release

## Goal

Restore the UniFi Protect Bridge config form on Home Assistant 2026.7 and ship
a release-safe public compatibility package that preserves URL safety, removes
diagnostic leaks, and prevents the same compatibility gap from escaping CI.

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

The Protect host uses the same origin rules, while continuing to add `https://`
when the user enters a bare host. No webhook event, Protect automation,
credential-storage, sensor, or CLI behavior changes.

## Diagnostics privacy

Diagnostics will continue exposing useful counts, source names, models, and
state summaries. The config-entry title and detailed runtime/backfill/automation
error strings will be redacted because they can embed the configured Protect
host, username, URL, or NVR name. Error counts and non-sensitive status fields
remain available.

## CI and development dependencies

CI will retain the fast stub-based unit suite and add real Home Assistant smoke
jobs for the declared minimum release and the newest installable release. The
smoke job will serialize the complete config schema as Home Assistant does and
check the Home Assistant APIs used by the integration.

The development dependency floor moves to pytest 9.0.3 to remove
`PYSEC-2026-1845`. `voluptuous-serialize` becomes an explicit development
dependency so the regression test runs before Home Assistant is installed.

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
for a non-empty override. Align the package and integration metadata at version
`0.2.22` and prepare release notes. After local verification, review the diff
and ask for explicit approval before pushing, merging, releasing, commenting,
or closing GitHub items.

Shared Home Assistant sessions, resync concurrency changes, selector migration,
95%+ total coverage, Dependabot, action pinning, and GitHub security-setting
changes are intentionally deferred to a separate hardening release.

## README documentation addendum

Before publication, update the existing README without restructuring it. The
public documentation must:

- explain that a bare Protect host defaults to HTTPS and that explicit Protect
  and webhook values must be clean HTTP(S) origins without credentials, paths,
  queries, fragments, backslashes, whitespace, or malformed ports;
- add a pre-publication `0.2.22` upgrade note describing the Home Assistant
  2026.7 config-flow fix and clarifying that existing entries need no migration,
  without claiming the version has already been released;
- align the diagnostics section with the expanded title and detailed-error
  redaction while retaining useful non-sensitive counters; and
- turn the manual-install destination into complete copy, restart, and setup
  instructions.

Do not describe `0.2.22` as already released. Preserve the verified CLI
`v0.1.5` example and the existing feature, entity, event, and service sections.
