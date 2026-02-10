"""Faster Whisper Speech-to-Text provider (local, free, faster than original)."""

from pathlib import Path
from typing import Optional, Union
import numpy as np

from .base import BaseSTT


class FasterWhisperSTT(BaseSTT):
    """
    Speech-to-Text using Faster Whisper (CTranslate2 backend).

    Faster than original Whisper, same accuracy. Runs locally, no API key required.

    Models (speed vs accuracy trade-off):
    - tiny: Fastest, least accurate
    - base: Good balance
    - small: Better accuracy
    - medium: High accuracy
    - large-v3: Best accuracy

    Usage:
        stt = FasterWhisperSTT(model="base")
        text = stt.transcribe("audio.mp3")
    """

    def __init__(
        self,
        model: str = "base",
        device: str = "auto",
        compute_type: str = "auto",
        download_root: Optional[str] = None,
    ):
        """
        Initialize Faster Whisper STT.

        Args:
            model: Model size (tiny, base, small, medium, large-v3)
            device: Device to use (auto, cpu, cuda)
            compute_type: Computation type (auto, int8, float16, float32)
            download_root: Directory to download models to
        """
        self.model_name = model
        self.device = device
        self.compute_type = compute_type
        self.download_root = download_root
        self._model = None

    def _load_model(self):
        """Lazy load the Faster Whisper model."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                raise ImportError(
                    "faster-whisper not installed. Install with: pip install faster-whisper"
                )

            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
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
            # Faster-whisper expects float32 audio normalized to [-1, 1]
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            if audio.max() > 1.0:
                audio = audio / 32768.0  # Convert from int16 range

        segments, info = model.transcribe(
            audio if isinstance(audio, np.ndarray) else str(audio),
            **options
        )

        # Collect all segments
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)

        return " ".join(text_parts).strip()

    def transcribe_stream(self, audio_stream) -> str:
        """
        Transcribe streaming audio.

        Note: Collects chunks and transcribes when complete.

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
        """Check if faster-whisper is installed."""
        try:
            from faster_whisper import WhisperModel
            return True
        except ImportError:
            return False
