#!/usr/bin/env python3
"""
Voice interface for Claude Code.

Listens for voice input, sends to Claude Code CLI, speaks the response.

Usage:
    python voice_claude.py [--cwd /path/to/project]

Example:
    cd /Users/medisiva/Desktop/mycoding/voice-toolkit
    python voice_claude.py --cwd /Users/medisiva/Desktop/mycoding/animation
"""

import argparse
import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Add voice_toolkit to path if running from source
sys.path.insert(0, str(Path(__file__).parent))

from voice_toolkit.stt import FasterWhisperSTT
from voice_toolkit.stt.whisper_stt import MicrophoneRecorder
from voice_toolkit.tts import EdgeTTS


class VoiceClaude:
    """Voice interface for Claude Code."""

    def __init__(self, cwd: str = None, model: str = "base"):
        self.cwd = cwd or os.getcwd()
        self.stt = FasterWhisperSTT(model=model)
        self.tts = EdgeTTS(voice="aria")
        self.recorder = MicrophoneRecorder()

        print(f"Working directory: {self.cwd}")
        print("Loading Whisper model...")
        # Warm up the model
        self.stt._load_model()
        print("Ready!")

    def listen(self) -> str:
        """Listen for voice input and return transcribed text."""
        print("\n🎤 Listening... (speak now)")
        audio = self.recorder.record_until_silence(
            silence_threshold=0.01,
            silence_duration=1.5,
            max_duration=30.0,
        )

        print("🔄 Transcribing...")
        text = self.stt.transcribe(audio)
        return text.strip()

    def send_to_claude(self, text: str) -> str:
        """Send text to Claude Code and get response."""
        print(f"📤 Sending to Claude: {text}")

        try:
            # Use claude CLI with --print flag for non-interactive mode
            result = subprocess.run(
                ["claude", "-p", text],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            response = result.stdout.strip()
            if result.returncode != 0 and result.stderr:
                response = f"Error: {result.stderr.strip()}"

            return response

        except subprocess.TimeoutExpired:
            return "Claude took too long to respond."
        except FileNotFoundError:
            return "Claude CLI not found. Make sure it's installed and in your PATH."
        except Exception as e:
            return f"Error running Claude: {e}"

    async def speak(self, text: str):
        """Speak the response."""
        # Truncate very long responses for speech
        if len(text) > 500:
            spoken_text = text[:500] + "... (response truncated for speech)"
        else:
            spoken_text = text

        print(f"🔊 Speaking response...")
        await self.tts.speak_async(spoken_text)

    async def run_once(self) -> bool:
        """Run one voice interaction. Returns False to exit."""
        text = self.listen()

        if not text:
            print("(no speech detected)")
            return True

        print(f"\n>>> You said: {text}")

        # Check for exit commands
        lower_text = text.lower()
        if any(cmd in lower_text for cmd in ["exit", "quit", "stop", "goodbye", "bye"]):
            await self.speak("Goodbye!")
            return False

        # Send to Claude
        response = self.send_to_claude(text)

        print(f"\n<<< Claude: {response}\n")

        # Speak response
        await self.speak(response)

        return True

    async def run(self):
        """Run the voice assistant loop."""
        print("\n" + "=" * 60)
        print("🎙️  Voice Claude - Speak to interact with Claude Code")
        print("=" * 60)
        print("Commands:")
        print("  • Speak naturally to ask Claude anything")
        print("  • Say 'exit' or 'quit' to stop")
        print("  • Press Ctrl+C to force quit")
        print("=" * 60)

        await self.speak("Voice Claude ready. How can I help you?")

        try:
            while True:
                should_continue = await self.run_once()
                if not should_continue:
                    break
        except KeyboardInterrupt:
            print("\n\nStopped by user.")


def main():
    parser = argparse.ArgumentParser(description="Voice interface for Claude Code")
    parser.add_argument(
        "--cwd",
        type=str,
        default=None,
        help="Working directory for Claude Code (default: current directory)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: base)"
    )

    args = parser.parse_args()

    voice_claude = VoiceClaude(cwd=args.cwd, model=args.model)
    asyncio.run(voice_claude.run())


if __name__ == "__main__":
    main()
