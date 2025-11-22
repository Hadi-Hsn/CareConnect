"""Authentication endpoints."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserLoginPhone, UserResponse
from app.services.whatsapp_service import get_whatsapp_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Register a new user."""
    # Check if user exists by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if phone number already exists
    result = await db.execute(
        select(User).where(
            User.phone == user_data.phone,
            User.country_code == user_data.country_code
        )
    )
    existing_phone = result.scalar_one_or_none()

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)

    user = User(
        email=user_data.email,
        name=user_data.name,
        phone=user_data.phone,
        country_code=user_data.country_code,
        role=user_data.role,
        hashed_password=hashed_password,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info("user_registered", user_id=user.id, email=user.email, role=user.role, phone=user.full_phone_number)

    # Send welcome message via WhatsApp
    try:
        whatsapp_service = get_whatsapp_service()
        await whatsapp_service.send_welcome_message(user.full_phone_number, user.name)
        logger.info("welcome_whatsapp_sent", user_id=user.id)
    except Exception as e:
        # Don't fail registration if WhatsApp fails
        logger.warning("welcome_whatsapp_failed", user_id=user.id, error=str(e))

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1440 * 60,  # 1 day in seconds
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Login user with email."""
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    logger.info("user_logged_in", user_id=user.id, email=user.email)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1440 * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login/phone", response_model=TokenResponse)
async def login_phone(credentials: UserLoginPhone, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Login user with phone number."""
    # Find user by phone and country code
    result = await db.execute(
        select(User).where(
            User.phone == credentials.phone,
            User.country_code == credentials.country_code
        )
    )
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password",
        )

    logger.info("user_logged_in_phone", user_id=user.id, phone=user.full_phone_number)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1440 * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/token", response_model=TokenResponse)
async def get_token(credentials: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """OAuth2 compatible token endpoint."""
    return await login(credentials, db)
