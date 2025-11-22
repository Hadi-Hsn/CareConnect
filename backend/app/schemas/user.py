"""User schemas."""
from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole


# Common country codes for validation
COUNTRY_CODES = [
    "+1", "+7", "+20", "+27", "+30", "+31", "+32", "+33", "+34", "+36", "+39", "+40",
    "+41", "+43", "+44", "+45", "+46", "+47", "+48", "+49", "+51", "+52", "+53", "+54",
    "+55", "+56", "+57", "+58", "+60", "+61", "+62", "+63", "+64", "+65", "+66", "+81",
    "+82", "+84", "+86", "+90", "+91", "+92", "+93", "+94", "+95", "+98", "+212", "+213",
    "+216", "+218", "+220", "+221", "+222", "+223", "+224", "+225", "+226", "+227", "+228",
    "+229", "+230", "+231", "+232", "+233", "+234", "+235", "+236", "+237", "+238", "+239",
    "+240", "+241", "+242", "+243", "+244", "+245", "+246", "+248", "+249", "+250", "+251",
    "+252", "+253", "+254", "+255", "+256", "+257", "+258", "+260", "+261", "+262", "+263",
    "+264", "+265", "+266", "+267", "+268", "+269", "+290", "+291", "+297", "+298", "+299",
    "+350", "+351", "+352", "+353", "+354", "+355", "+356", "+357", "+358", "+359", "+370",
    "+371", "+372", "+373", "+374", "+375", "+376", "+377", "+378", "+380", "+381", "+382",
    "+383", "+385", "+386", "+387", "+389", "+420", "+421", "+423", "+500", "+501", "+502",
    "+503", "+504", "+505", "+506", "+507", "+508", "+509", "+590", "+591", "+592", "+593",
    "+594", "+595", "+596", "+597", "+598", "+599", "+670", "+672", "+673", "+674", "+675",
    "+676", "+677", "+678", "+679", "+680", "+681", "+682", "+683", "+685", "+686", "+687",
    "+688", "+689", "+690", "+691", "+692", "+850", "+852", "+853", "+855", "+856", "+880",
    "+886", "+960", "+961", "+962", "+963", "+964", "+965", "+966", "+967", "+968", "+970",
    "+971", "+972", "+973", "+974", "+975", "+976", "+977", "+992", "+993", "+994", "+995",
    "+996", "+998"
]


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str = Field(..., description="Password confirmation must match password")
    phone: str = Field(..., min_length=7, max_length=20, description="Phone number (required)")
    country_code: str = Field(default="+961", description="Country code (e.g., +961 for Lebanon)")
    role: UserRole = UserRole.PATIENT

    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate country code format."""
        if not v:
            raise ValueError('Country code is required')
        
        # Ensure it starts with +
        if not v.startswith('+'):
            v = '+' + v
        
        # Validate format: + followed by 1-3 digits
        if not re.match(r'^\+\d{1,4}$', v):
            raise ValueError('Country code must be in format +XXX (e.g., +961)')
        
        # Check if it's a valid country code
        if v not in COUNTRY_CODES:
            raise ValueError(f'Invalid country code: {v}')
        
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        if not v:
            raise ValueError('Phone number is required')
        
        # Remove common separators and spaces
        cleaned = re.sub(r'[\s\-\(\)\.]', '', v)
        
        # Remove leading + or 00 if present (country code should be separate)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        if cleaned.startswith('00'):
            cleaned = cleaned[2:]
        
        # Check that it contains only digits
        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits (after removing separators)')
        
        # Check minimum length (at least 7 digits for local number)
        if len(cleaned) < 7:
            raise ValueError('Phone number must contain at least 7 digits')
        
        # Check maximum length
        if len(cleaned) > 15:
            raise ValueError('Phone number cannot exceed 15 digits')
        
        return cleaned

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
    phone: str | None = Field(None, min_length=7, max_length=20)
    country_code: str | None = None

    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Validate country code format."""
        if v is None:
            return v
        
        if not v.startswith('+'):
            v = '+' + v
        
        if not re.match(r'^\+\d{1,4}$', v):
            raise ValueError('Country code must be in format +XXX (e.g., +961)')
        
        if v not in COUNTRY_CODES:
            raise ValueError(f'Invalid country code: {v}')
        
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate phone number format."""
        if v is None:
            return v
        
        cleaned = re.sub(r'[\s\-\(\)\.]', '', v)
        
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        if cleaned.startswith('00'):
            cleaned = cleaned[2:]
        
        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits')
        
        if len(cleaned) < 7:
            raise ValueError('Phone number must contain at least 7 digits')
        
        if len(cleaned) > 15:
            raise ValueError('Phone number cannot exceed 15 digits')
        
        return cleaned


class UserResponse(UserBase):
    """User response schema."""

    id: int
    role: UserRole
    phone: str
    country_code: str
    whatsapp_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
    
    @property
    def full_phone_number(self) -> str:
        """Get full international phone number."""
        return f"{self.country_code}{self.phone}"


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserLoginPhone(BaseModel):
    """User login schema using phone number."""

    phone: str = Field(..., min_length=7, max_length=20)
    country_code: str = Field(default="+961")
    password: str

    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate country code format."""
        if not v.startswith('+'):
            v = '+' + v
        if not re.match(r'^\+\d{1,4}$', v):
            raise ValueError('Country code must be in format +XXX')
        if v not in COUNTRY_CODES:
            raise ValueError(f'Invalid country code: {v}')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        cleaned = re.sub(r'[\s\-\(\)\.]', '', v)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        if cleaned.startswith('00'):
            cleaned = cleaned[2:]
        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits')
        if len(cleaned) < 7:
            raise ValueError('Phone number must contain at least 7 digits')
        return cleaned


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
