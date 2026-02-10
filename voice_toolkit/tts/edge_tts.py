"""Edge TTS provider (free, requires internet)."""

import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union

from .base import BaseTTS


class EdgeTTS(BaseTTS):
    """
    Text-to-Speech using Microsoft Edge TTS (free, online).

    Uses Microsoft's neural TTS voices via edge-tts library.
    No API key required, but needs internet connection.

    Installation:
        pip install edge-tts

    Usage:
        tts = EdgeTTS(voice="en-US-AriaNeural")
        tts.speak("Hello world")  # Plays audio
        await tts.speak_async("Hello world", "output.mp3")  # Saves to file
    """

    # Common voice options
    VOICES = {
        # US English
        "aria": "en-US-AriaNeural",      # Female, conversational
        "guy": "en-US-GuyNeural",        # Male, newscast
        "jenny": "en-US-JennyNeural",    # Female, friendly
        "tony": "en-US-TonyNeural",      # Male, friendly
        # UK English
        "sonia": "en-GB-SoniaNeural",    # Female, British
        "ryan": "en-GB-RyanNeural",      # Male, British
        # Kids voices (great for children's content)
        "ana": "en-US-AnaNeural",        # Female, child-like
    }

    def __init__(
        self,
        voice: str = "en-US-AriaNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ):
        """
        Initialize Edge TTS.

        Args:
            voice: Voice name or shorthand (aria, guy, jenny, etc.)
            rate: Speaking rate adjustment (e.g., "+20%", "-10%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
        """
        # Allow shorthand voice names
        self.voice = self.VOICES.get(voice, voice)
        self.rate = rate
        self.pitch = pitch

    def speak(
        self,
        text: str,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Optional[Path]:
        """
        Convert text to speech (synchronous wrapper).

        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file.
                        If None, plays audio directly.

        Returns:
            Path to saved audio file, or None if played directly
        """
        return asyncio.get_event_loop().run_until_complete(
            self.speak_async(text, output_path)
        )

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
        try:
            import edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts not installed. Install with: pip install edge-tts"
            )

        # Generate to temp file if playing directly
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = Path(f.name)
            await self._generate(text, temp_path)
            await self._play_audio_async(temp_path)
            temp_path.unlink()  # Clean up
            return None
        else:
            output_path = Path(output_path)
            await self._generate(text, output_path)
            return output_path

    async def _generate(self, text: str, output_path: Path) -> None:
        """Generate audio file from text."""
        import edge_tts

        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch,
        )
        await communicate.save(str(output_path))

    async def _play_audio_async(self, audio_path: Path) -> None:
        """Play audio file asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._play_audio, audio_path)

    def _play_audio(self, audio_path: Path) -> None:
        """Play audio file."""
        try:
            import sounddevice as sd
            import soundfile as sf

            data, samplerate = sf.read(str(audio_path))
            sd.play(data, samplerate)
            sd.wait()
        except ImportError:
            # Fallback to system command
            import platform
            system = platform.system()

            if system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_path)])
            elif system == "Linux":
                subprocess.run(["mpg123", str(audio_path)])
            elif system == "Windows":
                subprocess.run(["start", str(audio_path)], shell=True)

    def is_available(self) -> bool:
        """Check if edge-tts is installed."""
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    @classmethod
    async def list_voices(cls, language: str = "en") -> list:
        """
        List available voices for a language.

        Args:
            language: Language code prefix (e.g., "en", "es", "fr")

        Returns:
            List of voice dictionaries with Name, Gender, Locale
        """
        import edge_tts
        voices = await edge_tts.list_voices()
        return [v for v in voices if v["Locale"].startswith(language)]
