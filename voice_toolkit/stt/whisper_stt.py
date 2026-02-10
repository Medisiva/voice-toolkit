"""Whisper Speech-to-Text provider (local, free)."""

import tempfile
from pathlib import Path
from typing import Optional, Union
import numpy as np

from .base import BaseSTT


class WhisperSTT(BaseSTT):
    """
    Speech-to-Text using OpenAI's Whisper model.

    Runs locally, no API key required. Free and private.

    Models (speed vs accuracy trade-off):
    - tiny: Fastest, least accurate (~1GB VRAM)
    - base: Good balance (~1GB VRAM)
    - small: Better accuracy (~2GB VRAM)
    - medium: High accuracy (~5GB VRAM)
    - large: Best accuracy (~10GB VRAM)

    Usage:
        stt = WhisperSTT(model="base")
        text = stt.transcribe("audio.mp3")
        # or
        text = stt.transcribe(audio_numpy_array)
    """

    def __init__(
        self,
        model: str = "base",
        device: Optional[str] = None,
        download_root: Optional[str] = None,
    ):
        """
        Initialize Whisper STT.

        Args:
            model: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cuda, cpu, or None for auto)
            download_root: Directory to download models to
        """
        self.model_name = model
        self.device = device
        self.download_root = download_root
        self._model = None

    def _load_model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            try:
                import whisper
            except ImportError:
                raise ImportError(
                    "Whisper not installed. Install with: pip install openai-whisper"
                )

            self._model = whisper.load_model(
                self.model_name,
                device=self.device,
                download_root=self.download_root,
            )
        return self._model

    def transcribe(
        self,
        audio: Union[str, Path, np.ndarray],
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio to text.

        Args:
            audio: Path to audio file or numpy array (16kHz, mono, float32)
            language: Optional language code (e.g., 'en', 'es', 'fr')

        Returns:
            Transcribed text
        """
        model = self._load_model()

        options = {}
        if language:
            options["language"] = language

        # Handle numpy array input
        if isinstance(audio, np.ndarray):
            # Whisper expects float32 audio normalized to [-1, 1]
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            if audio.max() > 1.0:
                audio = audio / 32768.0  # Convert from int16 range

            result = model.transcribe(audio, **options)
        else:
            # File path
            result = model.transcribe(str(audio), **options)

        return result["text"].strip()

    def transcribe_stream(self, audio_stream) -> str:
        """
        Transcribe streaming audio.

        Note: Whisper doesn't natively support streaming.
        This collects chunks and transcribes when complete.

        Args:
            audio_stream: Generator yielding audio chunks (numpy arrays)

        Returns:
            Transcribed text
        """
        # Collect all audio chunks
        chunks = list(audio_stream)
        if not chunks:
            return ""

        # Concatenate chunks
        audio = np.concatenate(chunks)
        return self.transcribe(audio)

    def is_available(self) -> bool:
        """Check if Whisper is installed."""
        try:
            import whisper
            return True
        except ImportError:
            return False


class MicrophoneRecorder:
    """
    Helper class to record audio from microphone.

    Usage:
        recorder = MicrophoneRecorder()
        audio = recorder.record(duration=5)
        # or
        with recorder.record_until_silence() as audio:
            text = stt.transcribe(audio)
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device: Optional[int] = None,
    ):
        """
        Initialize microphone recorder.

        Args:
            sample_rate: Audio sample rate (Whisper expects 16000)
            channels: Number of audio channels (1 for mono)
            device: Input device index (None for default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

    def record(self, duration: float) -> np.ndarray:
        """
        Record audio for a fixed duration.

        Args:
            duration: Recording duration in seconds

        Returns:
            Numpy array of audio data (float32, 16kHz)
        """
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError(
                "sounddevice not installed. Install with: pip install sounddevice"
            )

        print(f"Recording for {duration} seconds...")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32,
            device=self.device,
        )
        sd.wait()
        print("Recording complete.")

        return audio.flatten()

    def record_until_silence(
        self,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,
        max_duration: float = 30.0,
    ) -> np.ndarray:
        """
        Record audio until silence is detected.

        Args:
            silence_threshold: RMS threshold for silence detection
            silence_duration: Seconds of silence to stop recording
            max_duration: Maximum recording duration

        Returns:
            Numpy array of audio data
        """
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError(
                "sounddevice not installed. Install with: pip install sounddevice"
            )

        chunk_duration = 0.1  # 100ms chunks
        chunk_samples = int(chunk_duration * self.sample_rate)
        silence_chunks = int(silence_duration / chunk_duration)
        max_chunks = int(max_duration / chunk_duration)

        chunks = []
        silent_count = 0

        print("Recording... (speak now, will stop after silence)")

        for i in range(max_chunks):
            chunk = sd.rec(
                chunk_samples,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                device=self.device,
            )
            sd.wait()
            chunks.append(chunk.flatten())

            # Check for silence
            rms = np.sqrt(np.mean(chunk**2))
            if rms < silence_threshold:
                silent_count += 1
                if silent_count >= silence_chunks and len(chunks) > silence_chunks:
                    print("Silence detected, stopping.")
                    break
            else:
                silent_count = 0

        print("Recording complete.")
        return np.concatenate(chunks)
