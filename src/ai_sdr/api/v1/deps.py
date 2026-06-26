"""FastAPI dependencies — DB session, auth, etc."""

from collections.abc import AsyncGenerator

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.config import settings
from ai_sdr.db.session import get_session

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async for session in get_session():
        yield session


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Verify API key if one is configured. Skip auth if no key is set."""
    if not settings.API_KEY:
        return "no-auth"
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
