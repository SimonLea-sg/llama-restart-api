# auth.py
from typing import Optional
from fastapi import HTTPException
from config import AppSettings

def verify_api_key(app_settings: AppSettings, x_api_key: Optional[str] = None) -> None:
    """
    Verify that a supplied API key is valid.
    If no API keys are configured, authentication is disabled.
    """
    # If no API keys are configured, disable authentication.
    if not app_settings.api_keys:
        return

    # If a header is supplied, verify it.
    if x_api_key is None:
        # This situation occurs for endpoints that allow unauthenticated access
        # (e.g., /health).  No verification is needed.
        return

    # Verify that the supplied header matches one of the configured keys.
    # `app_settings.api_keys` is a List[str]; `in` works directly on the list.
    if x_api_key not in app_settings.api_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

