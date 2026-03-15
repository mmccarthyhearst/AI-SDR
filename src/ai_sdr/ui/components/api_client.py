"""Thin httpx wrapper for calling the FastAPI backend from Streamlit."""
import os
from typing import Any

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["X-API-Key"] = API_KEY
    return h


def get(path: str, params: dict | None = None) -> Any:
    """GET request. Returns parsed JSON or {"error": ...} on failure."""
    try:
        resp = httpx.get(
            f"{API_BASE_URL}{path}", params=params, headers=_headers(), timeout=10.0
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def post(path: str, data: dict) -> Any:
    """POST request. Returns parsed JSON or {"error": ...} on failure."""
    try:
        resp = httpx.post(
            f"{API_BASE_URL}{path}", json=data, headers=_headers(), timeout=30.0
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def patch(path: str, data: dict) -> Any:
    """PATCH request. Returns parsed JSON or {"error": ...} on failure."""
    try:
        resp = httpx.patch(
            f"{API_BASE_URL}{path}", json=data, headers=_headers(), timeout=10.0
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}
