#!/usr/bin/env python3
"""
Claude Voice Interface Example

Voice interface for Claude Code - speak commands, hear responses.

Usage:
    python examples/claude_voice.py

Requirements:
    pip install voice-toolkit[all] anthropic
    export ANTHROPIC_API_KEY=your_key_here

Features:
    - Wake word activation ("hey claude")
    - Speaks Claude's responses
    - Can be integrated with Claude Code CLI
"""

import os
import sys

from voice_toolkit import VoiceAssistant
from voice_toolkit.stt import WhisperSTT
from voice_toolkit.tts import EdgeTTS  # Better quality for longer responses


def get_claude_response(text: str) -> str:
    """
    Get response from Claude API.

    For actual Claude Code integration, you would pipe to the CLI instead.
    """
    try:
        import anthropic
    except ImportError:
        return "Anthropic package not installed. Run: pip install anthropic"

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "Please set ANTHROPIC_API_KEY environment variable."

    client = anthropic.Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
        )
        return message.content[0].text
    except Exception as e:
        return f"Error calling Claude: {e}"


def main():
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not set.")
        print("Set it with: export ANTHROPIC_API_KEY=your_key_here")
        print()

    # Initialize STT (Whisper - local, free)
    print("Loading Whisper model (first run downloads ~140MB)...")
    stt = WhisperSTT(model="base")

    # Initialize TTS (Edge TTS - free, online, high quality)
    tts = EdgeTTS(voice="aria")  # Natural conversational voice

    # Create assistant with wake word
    assistant = VoiceAssistant(
        stt=stt,
        tts=tts,
        on_input=get_claude_response,
        wake_word="hey claude",  # Say "hey claude" to activate
        silence_duration=2.0,    # Longer pause tolerance for thinking
    )

    print()
    print("Claude Voice Interface")
    print("=" * 40)
    print("Say 'hey claude' followed by your question.")
    print("Example: 'Hey Claude, what's the weather like?'")
    print("Press Ctrl+C to stop.")
    print()

    # Start listening (blocking)
    assistant.start()


if __name__ == "__main__":
    main()
