import os

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Security constants
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "insecure-default-key-do-not-use-in-production")
JWT_ALGORITHM = "HS256"


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow login endpoint and docs to be accessed without token
        if (
            request.url.path == "/login"
            or request.url.path.startswith("/docs")
            or request.url.path.startswith("/openapi")
            or request.url.path.startswith("/metrics")
        ):
            return await call_next(request)

        # 1. Verify Authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401, content={"error": "Missing or invalid Authorization header"}
            )

        token = auth_header.split(" ")[1]
        try:
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"error": "Token has expired"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"error": "Invalid token"})

        return await call_next(request)
