from src.tenants import SAFE_ID

MIN_KEY_LENGTH = 16


def parse_api_keys(text: str) -> dict[str, str]:
    """Turn 'acme:key1,beta:key2' into {'acme': 'key1', 'beta': 'key2'}."""
    entries = [entry.strip() for entry in text.split(",") if entry.strip()]
    if not entries:
        raise ValueError("No API keys given")
    keys: dict[str, str] = {}
    for entry in entries:
        tenant, colon, key = entry.partition(":")
        tenant, key = tenant.strip(), key.strip()
        if not colon:
            raise ValueError("Each entry must look like tenant:key")
        if not SAFE_ID.fullmatch(tenant):
            raise ValueError(f"Invalid tenant name: {tenant!r}")
        if len(key) < MIN_KEY_LENGTH:
            raise ValueError(f"Keys must be at least {MIN_KEY_LENGTH} characters")
        keys[tenant] = key
    return keys
