from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="User Service", version="1.0.0")


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: str
    roles: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    roles: list[str] = Field(default_factory=lambda: ["user"])


_USERS: dict[UUID, User] = {}


@app.post("/users", response_model=User, status_code=201)
async def create_user(request: CreateUserRequest) -> User:
    user = User(email=request.email, name=request.name, roles=request.roles)
    _USERS[user.id] = user
    return user


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: UUID) -> User:
    user = _USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", response_model=list[User])
async def list_users(skip: int = 0, limit: int = 100) -> list[User]:
    return list(_USERS.values())[skip : skip + limit]


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "user-service"}
