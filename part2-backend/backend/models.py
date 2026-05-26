# API Data Transfer Objects: Outlines validation models and structural contracts for the Analyst Portal endpoints.

from typing import Optional
from pydantic import BaseModel, EmailStr


# Schema for structural frontend client credential login payloads
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Schema for context responses emitted upon successful login events
class LoginResponse(BaseModel):
    token: str
    user: "UserResponse"


# Schema for newly-provisioned administrative user profile definitions
class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "analyst"


# Schema for serialized identity contexts, strictly stripping password material
class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str

    class Config:
        from_attributes = True


# Schema for structural security incident alerting telemetry records
class EventResponse(BaseModel):
    id: str
    timestamp: str
    severity: str
    title: str
    description: str
    assetHostname: str
    assetIp: str
    sourceIp: str
    tags: list
    userId: str