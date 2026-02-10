"""Piper Text-to-Speech provider (local, free, offline)."""

import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union

from .base import BaseTTS


class PiperTTS(BaseTTS):
    """
    Text-to-Speech using Piper (local, free, offline).

    Piper is a fast, local neural TTS system. No API key required.

    Installation:
        pip install piper-tts

    Or install piper binary:
        brew install piper (macOS)

    Usage:
        tts = PiperTTS(voice="en_US-amy-medium")
        tts.speak("Hello world")  # Plays audio
        tts.speak("Hello world", "output.wav")  # Saves to file
    """

    # Common voice models (download automatically on first use)
    VOICES = {
        "amy": "en_US-amy-medium",      # Female, American
        "ryan": "en_US-ryan-medium",    # Male, American
        "jenny": "en_GB-jenny_dioco-medium",  # Female, British
        "danny": "en_GB-danny-low",     # Male, British
    }

    def __init__(
        self,
        voice: str = "en_US-amy-medium",
        speed: float = 1.0,
        model_dir: Optional[str] = None,
    ):
        """
        Initialize Piper TTS.

        Args:
            voice: Voice model name or shorthand (amy, ryan, jenny, danny)
            speed: Speaking rate multiplier (0.5 = slow, 2.0 = fast)
            model_dir: Directory containing voice models
        """
        # Allow shorthand voice names
        self.voice = self.VOICES.get(voice, voice)
        self.speed = speed
        self.model_dir = model_dir
        self._piper_available = None

    def _check_piper(self) -> bool:
        """Check if piper is available."""
        if self._piper_available is None:
            try:
                # Try piper-tts Python package first
                import piper
                self._piper_available = "python"
            except ImportError:
                # Try piper binary
                try:
                    result = subprocess.run(
                        ["piper", "--version"],
                        capture_output=True,
                        text=True,
                    )
                    self._piper_available = "binary" if result.returncode == 0 else False
                except FileNotFoundError:
                    self._piper_available = False
        return bool(self._piper_available)

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
        if not self._check_piper():
            raise RuntimeError(
                "Piper not installed. Install with: pip install piper-tts"
            )

        # Generate to temp file if playing directly
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = Path(f.name)
            self._generate(text, temp_path)
            self._play_audio(temp_path)
            temp_path.unlink()  # Clean up
            return None
        else:
            output_path = Path(output_path)
            self._generate(text, output_path)
            return output_path

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
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.speak, text, output_path)

    def _generate(self, text: str, output_path: Path) -> None:
        """Generate audio file from text."""
        if self._piper_available == "python":
            self._generate_python(text, output_path)
        else:
            self._generate_binary(text, output_path)

    def _generate_python(self, text: str, output_path: Path) -> None:
        """Generate using piper-tts Python package."""
        import wave
        from piper import PiperVoice

        # Download voice model if needed
        voice = PiperVoice.load(self.voice)

        # Generate audio
        with wave.open(str(output_path), "wb") as wav_file:
            voice.synthesize(text, wav_file)

    def _generate_binary(self, text: str, output_path: Path) -> None:
        """Generate using piper binary."""
        cmd = [
            "piper",
            "--model", self.voice,
            "--output_file", str(output_path),
        ]

        if self.model_dir:
            cmd.extend(["--data-dir", self.model_dir])

        # Pipe text to piper
        result = subprocess.run(
            cmd,
            input=text,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Piper failed: {result.stderr}")

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
                subprocess.run(["aplay", str(audio_path)])
            elif system == "Windows":
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME)

    def is_available(self) -> bool:
        """Check if Piper is installed."""
        return self._check_piper()
