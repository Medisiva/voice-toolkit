"""Base class for Text-to-Speech providers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union


class BaseTTS(ABC):
    """
    Abstract base class for Text-to-Speech providers.

    Implement this interface to add new TTS providers.
    """

    @abstractmethod
    def speak(
        self,
        text: str,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Optional[Path]:
        """
        Convert text to speech.

        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file.
                        If None, plays audio directly.

        Returns:
            Path to saved audio file, or None if played directly
        """
        pass

    @abstractmethod
    async def speak_async(
        self,
        text: str,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Optional[Path]:
        """
        Convert text to speech asynchronously.

        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file.

        Returns:
            Path to saved audio file, or None if played directly
        """
        pass

    def is_available(self) -> bool:
        """Check if this TTS provider is available and configured."""
        return True
