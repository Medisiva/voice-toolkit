"""Base class for Speech-to-Text providers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union
import numpy as np


class BaseSTT(ABC):
    """
    Abstract base class for Speech-to-Text providers.

    Implement this interface to add new STT providers.
    """

    @abstractmethod
    def transcribe(
        self,
        audio: Union[str, Path, np.ndarray],
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio to text.

        Args:
            audio: Path to audio file or numpy array of audio data
            language: Optional language code (e.g., 'en', 'es')

        Returns:
            Transcribed text
        """
        pass

    @abstractmethod
    def transcribe_stream(self, audio_stream) -> str:
        """
        Transcribe streaming audio in real-time.

        Args:
            audio_stream: Generator or iterator yielding audio chunks

        Returns:
            Transcribed text
        """
        pass

    def is_available(self) -> bool:
        """Check if this STT provider is available and configured."""
        return True
