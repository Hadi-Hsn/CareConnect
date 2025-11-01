"""Voice API endpoints for text-to-speech and speech-to-text."""
import io
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.models.user import User
from app.services.voice_service import get_voice_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])


class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion."""

    text: str = Field(..., min_length=1, max_length=4096, description="Text to convert to speech")
    voice: str | None = Field(
        None,
        description="Voice to use (alloy, echo, fable, onyx, nova, shimmer)",
        pattern="^(alloy|echo|fable|onyx|nova|shimmer)$",
    )


class SpeechToTextResponse(BaseModel):
    """Response model for speech-to-text conversion."""

    text: str = Field(..., description="Transcribed text from audio")
    duration_seconds: float | None = Field(None, description="Audio duration in seconds")


@router.post(
    "/text-to-speech",
    response_class=StreamingResponse,
    summary="Convert text to speech",
    description="Convert text to speech using OpenAI TTS API. Returns audio in MP3 format.",
)
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    """
    Convert text to speech and return audio stream.

    Args:
        request: Text to speech request
        current_user: Authenticated user

    Returns:
        Audio stream in MP3 format
    """
    try:
        voice_service = get_voice_service()
        audio_bytes = await voice_service.text_to_speech(
            text=request.text,
            voice=request.voice,
        )

        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="speech.mp3"',
                "Cache-Control": "no-cache",
            },
        )

    except Exception as e:
        logger.error(f"Text-to-speech error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech conversion failed: {str(e)}")


@router.post(
    "/speech-to-text",
    response_model=SpeechToTextResponse,
    summary="Convert speech to text",
    description="Convert audio to text using OpenAI Whisper API. Supports various audio formats.",
)
async def speech_to_text(
    current_user: Annotated[User, Depends(get_current_user)],
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = Form("en", description="Language code (e.g., en, es, fr)"),
) -> SpeechToTextResponse:
    """
    Convert speech to text from uploaded audio file.

    Args:
        current_user: Authenticated user
        audio: Audio file upload
        language: Language code for transcription

    Returns:
        Transcribed text
    """
    try:
        # Validate file size (max 25MB)
        contents = await audio.read()
        if len(contents) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")

        # Create file-like object
        audio_file = io.BytesIO(contents)

        voice_service = get_voice_service()
        transcribed_text = await voice_service.speech_to_text(
            audio_file=audio_file,
            filename=audio.filename or "audio.webm",
            language=language,
        )

        return SpeechToTextResponse(
            text=transcribed_text,
            duration_seconds=None,  # Could calculate this if needed
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text conversion failed: {str(e)}")
