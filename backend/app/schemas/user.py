"""User schemas."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str = Field(..., description="Password confirmation must match password")
    phone: str | None = Field(None, min_length=10, max_length=20, description="Phone number")
    role: UserRole = UserRole.PATIENT

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate phone number format."""
        if v is None:
            return v
        # Remove common separators
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 10:
            raise ValueError('Phone number must contain at least 10 digits')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'UserCreate':
        """Validate that password and confirm_password match."""
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class UserUpdate(BaseModel):
    """User update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None


class UserResponse(UserBase):
    """User response schema."""

    id: int
    role: UserRole
    phone: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
