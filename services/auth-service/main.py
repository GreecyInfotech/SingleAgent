from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Auth Service", version="1.0.0")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "auth-service-secret-key-change-in-production"
ALGORITHM = "HS256"


class UserCredentials(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str
    email: str
    roles: list[str] = Field(default_factory=list)
    exp: datetime


# In-memory user store (replace with database)
_USERS: dict[str, dict[str, Any]] = {
    "admin@enterprise.com": {
        "id": str(uuid4()),
        "email": "admin@enterprise.com",
        "password_hash": pwd_context.hash("admin123"),
        "roles": ["admin", "agent_operator"],
    }
}


@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserCredentials) -> TokenResponse:
    user = _USERS.get(credentials.email)
    if not user or not pwd_context.verify(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    expires = datetime.now(UTC) + timedelta(hours=1)
    token = jwt.encode(
        {"sub": user["id"], "email": user["email"], "roles": user["roles"], "exp": expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return TokenResponse(access_token=token, expires_in=3600)


@app.post("/auth/verify")
async def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "payload": payload}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "auth-service"}
