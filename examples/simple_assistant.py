#!/usr/bin/env python3
"""
Simple Voice Assistant Example

Demonstrates basic voice interaction with echo response.

Usage:
    python examples/simple_assistant.py

Requirements:
    pip install voice-toolkit[all]
    # or
    pip install openai-whisper piper-tts sounddevice
"""

from voice_toolkit import VoiceAssistant
from voice_toolkit.stt import WhisperSTT
from voice_toolkit.tts import PiperTTS


def echo_handler(text: str) -> str:
    """Simple echo handler - returns what was said."""
    return f"You said: {text}"


def main():
    # Initialize STT (Whisper - local, free)
    stt = WhisperSTT(model="base")  # Options: tiny, base, small, medium, large

    # Initialize TTS (Piper - local, free)
    tts = PiperTTS(voice="amy")  # Options: amy, ryan, jenny, danny

    # Create assistant
    assistant = VoiceAssistant(
        stt=stt,
        tts=tts,
        on_input=echo_handler,
        silence_duration=1.5,  # Stop listening after 1.5s of silence
    )

    print("Simple Voice Assistant")
    print("=" * 40)
    print("Speak and I'll echo back what you said.")
    print("Press Ctrl+C to stop.")
    print()

    # Start listening (blocking)
    assistant.start()


if __name__ == "__main__":
    main()
