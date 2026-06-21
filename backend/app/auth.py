"""
API key authentication.

Simple, stateless, and honest about what it is: a shared secret in an
HTTP header, not a full auth system. In an interview, say exactly that:
"It's a single shared API key loaded from an environment variable --
appropriate for a controlled demo environment, but in production I'd
replace this with JWT tokens and per-user auth, since that gives you
per-user revocation and audit trails."

Knowing what your solution ISN'T designed for is as important as knowing
what it is.
"""
import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Loaded from environment so it never appears in source code.
# Default is "dev-secret" ONLY for local development convenience --
# the Dockerfile/CI should always override this via environment variable.
_VALID_API_KEY = os.getenv("API_KEY", "dev-secret")


def require_api_key(api_key: str = Security(_api_key_header)):
    """
    FastAPI dependency. Add to any route or router with:
        dependencies=[Depends(require_api_key)]

    Or to all routes at once in main.py's app instantiation.
    """
    if api_key != _VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key. Pass X-API-Key header.",
        )
    return api_key
