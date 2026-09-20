"""Core API schemas."""
import re
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=128)
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.casefold()
        if not EMAIL_PATTERN.fullmatch(value): raise ValueError("must be a valid email address")
        return value

class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str: return value.casefold()

class AccountResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class ValidationResponse(BaseModel):
    valid: bool = True
    account: AccountResponse
    expires_at: datetime

UserCreate = RegisterRequest
UserResponse = AccountResponse
