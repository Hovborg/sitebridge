from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit


class InvalidOrigin(ValueError):
    """An HTTP(S) origin is malformed or contains disallowed components."""


def normalize_http_origin(
    value: Any,
    *,
    default_scheme: str | None = None,
) -> str:
    """Return a normalized HTTP(S) origin without path, query, or credentials."""
    text = str(value or "").strip()
    if not text:
        raise InvalidOrigin("origin is empty")
    if any(
        character.isspace()
        or ord(character) < 32
        or ord(character) == 127
        or character == "\\"
        for character in text
    ):
        raise InvalidOrigin("origin contains invalid characters")
    if "://" not in text:
        if default_scheme not in {"http", "https"}:
            raise InvalidOrigin("origin must include http:// or https://")
        text = f"{default_scheme}://{text}"

    try:
        parsed = urlsplit(text)
        _port = parsed.port
    except ValueError as err:
        raise InvalidOrigin("origin has an invalid host or port") from err

    if parsed.scheme not in {"http", "https"} or parsed.hostname is None:
        raise InvalidOrigin("origin must use http or https and include a host")
    if parsed.username is not None or parsed.password is not None:
        raise InvalidOrigin("origin must not include credentials")
    if parsed.netloc.endswith(":"):
        raise InvalidOrigin("origin has an empty port")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise InvalidOrigin("origin must not include a path, query, or fragment")

    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
