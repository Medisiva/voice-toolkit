"""Speech-to-Text providers."""

from .base import BaseSTT
from .whisper_stt import WhisperSTT

__all__ = ["BaseSTT", "WhisperSTT"]
