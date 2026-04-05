# Repo Split

## Conclusion

Yes, the architecture should be split.

## Why

### HACS constraint

HACS says an integration repository must contain only one integration under `custom_components/`, and all files required for the integration to run must live inside that integration directory.

### Product boundaries

Ubiquiti documents separate API surfaces for Site Manager, local UniFi applications, and app-specific features like Protect and Access.

### Home Assistant boundaries

Home Assistant also keeps UniFi Network and UniFi Protect as separate integrations.

## Practical result

This repo becomes the HA Protect bridge first.

Later split:

- Repo A: HACS custom integration (`ha_protect_bridge`)
- Repo B: shared Python client / CLI

For now, keeping them conceptually split inside one private repo is acceptable while the webhook model is still proving itself.
