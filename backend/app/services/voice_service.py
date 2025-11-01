"""Voice service using OpenAI TTS and Whisper for speech-to-text."""
import io
import logging
from typing import BinaryIO

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VoiceService:
    """Service for text-to-speech and speech-to-text using OpenAI."""

    def __init__(self):
        """Initialize the voice service."""
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.tts_model = settings.openai_tts_model
        self.tts_voice = settings.openai_tts_voice
        self.stt_model = settings.openai_stt_model

    async def text_to_speech(self, text: str, voice: str | None = None) -> bytes:
        """
        Convert text to speech using OpenAI TTS.

        Args:
            text: The text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            Audio data as bytes in MP3 format

        Raises:
            Exception: If TTS conversion fails
        """
        try:
            logger.info(f"Converting text to speech: {text[:50]}...")
            
            response = await self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice or self.tts_voice,
                input=text,
                response_format="mp3",
            )

            # Get audio bytes
            audio_bytes = response.content
            logger.info(f"Successfully generated {len(audio_bytes)} bytes of audio")
            
            return audio_bytes

        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            raise

    async def speech_to_text(
        self,
        audio_file: BinaryIO,
        filename: str = "audio.webm",
        language: str = "en",
    ) -> str:
        """
        Convert speech to text using OpenAI Whisper.

        Args:
            audio_file: Audio file binary data
            filename: Name of the audio file
            language: Language code (default: en)

        Returns:
            Transcribed text

        Raises:
            Exception: If transcription fails
        """
        try:
            logger.info(f"Transcribing audio file: {filename}")
            
            # Create a file-like object with a name attribute
            audio_file.name = filename
            
            transcript = await self.client.audio.transcriptions.create(
                model=self.stt_model,
                file=audio_file,
                language=language,
            )

            transcribed_text = transcript.text
            logger.info(f"Successfully transcribed: {transcribed_text[:100]}...")
            
            return transcribed_text

        except Exception as e:
            logger.error(f"Speech-to-text error: {str(e)}")
            raise


# Singleton instance
_voice_service: VoiceService | None = None


def get_voice_service() -> VoiceService:
    """Get or create the voice service instance."""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
