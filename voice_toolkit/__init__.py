"""
Voice Toolkit - Modular STT/TTS library for building voice interfaces.

Usage:
    from voice_toolkit import VoiceAssistant
    from voice_toolkit.stt import WhisperSTT
    from voice_toolkit.tts import PiperTTS

    assistant = VoiceAssistant(
        stt=WhisperSTT(),
        tts=PiperTTS(),
        on_input=lambda text: "You said: " + text
    )
    assistant.start()
"""

from .assistant.voice_assistant import VoiceAssistant
from .stt import WhisperSTT, FasterWhisperSTT, BaseSTT
from .tts import PiperTTS, EdgeTTS, BaseTTS

__version__ = "0.1.0"
__all__ = [
    "VoiceAssistant",
    "WhisperSTT",
    "FasterWhisperSTT",
    "BaseSTT",
    "PiperTTS",
    "EdgeTTS",
    "BaseTTS",
]
