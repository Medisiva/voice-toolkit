#!/usr/bin/env python3
"""
Simple Voice Claude - uses claude -p with --continue for context.

Much more reliable than the pty approach.
"""

import argparse
import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))

from voice_toolkit.stt import FasterWhisperSTT
from voice_toolkit.stt.whisper_stt import MicrophoneRecorder
from voice_toolkit.tts import EdgeTTS


class SimpleVoiceClaude:
    """Simple voice interface for Claude Code."""

    def __init__(self, cwd: str = None, model: str = "small"):
        self.cwd = cwd or os.getcwd()
        self.stt = FasterWhisperSTT(model=model)
        self.tts = EdgeTTS(voice="aria")
        self.recorder = MicrophoneRecorder()

        print(f"Working directory: {self.cwd}")
        print("Loading Whisper model...")
        self.stt._load_model()
        print("Ready!\n")

    def listen(self) -> str:
        """Listen for voice input."""
        print("🎤 Listening... (speak now)")
        audio = self.recorder.record_until_silence(
            silence_threshold=0.005,
            silence_duration=1.5,
            max_duration=30.0,
        )

        print("🔄 Transcribing...")

        # Save to temp file for accurate transcription
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        sf.write(temp_path, audio, 16000)

        text = self.stt.transcribe(temp_path, language="en")
        os.unlink(temp_path)

        return text.strip()

    def send_to_claude(self, text: str) -> str:
        """Send to Claude Code and get response."""
        print(f"📤 Sending to Claude...")

        try:
            result = subprocess.run(
                ["claude", "-p", "--continue", text],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            response = result.stdout.strip()
            if result.returncode != 0 and not response:
                response = f"Error: {result.stderr.strip()}"

            return response

        except subprocess.TimeoutExpired:
            return "Claude took too long to respond."
        except Exception as e:
            return f"Error: {e}"

    async def speak(self, text: str):
        """Speak response (truncated for long responses)."""
        # Clean terminal codes
        import re
        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)

        if len(clean) > 500:
            clean = clean[:500] + "... check the terminal for the full response."

        if clean.strip():
            await self.tts.speak_async(clean)

    async def run(self):
        """Main loop."""
        print("=" * 60)
        print("🎙️  Simple Voice Claude")
        print("=" * 60)
        print("Speak to interact with Claude Code.")
        print("Context is preserved with --continue flag.")
        print("Say 'exit' or 'goodbye' to stop.")
        print("=" * 60 + "\n")

        await self.speak("Ready. What would you like to do?")

        while True:
            try:
                # Listen
                text = self.listen()

                if not text:
                    print("(no speech detected)\n")
                    continue

                print(f"\n>>> You: {text}\n")

                # Exit check
                if any(w in text.lower() for w in ["exit", "quit", "goodbye", "bye"]):
                    await self.speak("Goodbye!")
                    break

                # Send to Claude
                response = self.send_to_claude(text)

                print(f"<<< Claude:\n{response}\n")

                # Speak response
                await self.speak(response)

            except KeyboardInterrupt:
                print("\nStopped.")
                break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=str, default=None)
    parser.add_argument("--model", type=str, default="small")
    args = parser.parse_args()

    vc = SimpleVoiceClaude(cwd=args.cwd, model=args.model)
    asyncio.run(vc.run())


if __name__ == "__main__":
    main()
