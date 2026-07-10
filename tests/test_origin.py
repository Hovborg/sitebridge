import pytest

from custom_components.unifi_protect_bridge.origin import InvalidOrigin, normalize_http_origin


@pytest.mark.parametrize(
    "origin",
    (
        "http://\x00example.com",
        "http://example.com\x01",
        "http://example.com\x7f",
    ),
)
def test_normalize_http_origin_rejects_c0_and_del_controls(origin: str) -> None:
    with pytest.raises(InvalidOrigin, match="invalid characters"):
        normalize_http_origin(origin)
