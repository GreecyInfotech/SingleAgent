from fastapi import Request
from fastapi.responses import JSONResponse

from enterprise_agent_platform.core.exceptions import PlatformError

_STATUS_MAP = {
    "NOT_FOUND": 404,
    "VALIDATION_ERROR": 422,
    "AGENT_EXECUTION_ERROR": 500,
    "AUTHENTICATION_ERROR": 401,
    "AUTHORIZATION_ERROR": 403,
}


async def platform_error_handler(_request: Request, exc: PlatformError) -> JSONResponse:
    return JSONResponse(
        status_code=_STATUS_MAP.get(exc.code, 500),
        content={"code": exc.code, "message": exc.message, "details": exc.details},
    )
