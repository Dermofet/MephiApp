from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import config

class VersionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        version = request.headers.get("X-Api-Version", "0.0.1")
        if version not in config.API_VERSIONS:
            return JSONResponse(status_code=409, content={"details": "API version not found"})
        return await call_next(request)
