from fastapi import Header, HTTPException
from .config import settings
async def api_key_guard(x_api_key: str | None = Header(None)):
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
