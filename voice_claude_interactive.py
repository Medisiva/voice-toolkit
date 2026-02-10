#!/usr/bin/env python3
"""
Interactive Voice Claude - conversational voice interface.

Maintains a single Claude session for continuous conversation.

Usage:
    python voice_claude_interactive.py [--cwd /path/to/project]
"""

import argparse
import asyncio
import os
import pty
import select
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from voice_toolkit.stt import FasterWhisperSTT
from voice_toolkit.stt.whisper_stt import MicrophoneRecorder
from voice_toolkit.tts import EdgeTTS


class InteractiveVoiceClaude:
    """Interactive voice interface for Claude Code."""

    def __init__(self, cwd: str = None, model: str = "base"):
        self.cwd = cwd or os.getcwd()
        self.stt = FasterWhisperSTT(model=model)
        self.tts = EdgeTTS(voice="aria")
        self.recorder = MicrophoneRecorder()

        self.claude_process = None
        self.master_fd = None
        self.output_buffer = ""
        self.response_complete = threading.Event()
        self.listening = False

        print(f"Working directory: {self.cwd}")
        print("Loading Whisper model...")
        self.stt._load_model()
        print("Model loaded!")

    def start_claude(self):
        """Start Claude Code in interactive mode using pseudo-terminal."""
        print("Starting Claude Code session...")

        # Create pseudo-terminal
        master_fd, slave_fd = pty.openpty()
        self.master_fd = master_fd

        # Start Claude in the pty
        self.claude_process = subprocess.Popen(
            ["claude", "--continue"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=self.cwd,
            preexec_fn=os.setsid,
        )

        os.close(slave_fd)

        # Start output reader thread
        self.output_thread = threading.Thread(target=self._read_output, daemon=True)
        self.output_thread.start()

        # Wait for Claude to be ready
        time.sleep(2)
        print("Claude session started!")

    def _read_output(self):
        """Read output from Claude process."""
        while self.claude_process and self.claude_process.poll() is None:
            try:
                if select.select([self.master_fd], [], [], 0.1)[0]:
                    data = os.read(self.master_fd, 4096)
                    if data:
                        text = data.decode('utf-8', errors='ignore')
                        self.output_buffer += text
                        # Print Claude's output in real-time
                        sys.stdout.write(text)
                        sys.stdout.flush()
            except (OSError, IOError):
                break

    def send_to_claude(self, text: str):
        """Send text to Claude session."""
        if self.master_fd:
            # Clear buffer before sending
            self.output_buffer = ""
            # Send the message with newline
            os.write(self.master_fd, (text + "\n").encode())

    def wait_for_response(self, timeout: float = 60.0) -> str:
        """Wait for Claude to finish responding."""
        start = time.time()
        last_length = 0
        stable_count = 0

        while time.time() - start < timeout:
            time.sleep(0.5)
            current_length = len(self.output_buffer)

            # Check if output has stabilized (no new output for 2 seconds)
            if current_length == last_length and current_length > 0:
                stable_count += 1
                if stable_count >= 4:  # 2 seconds of stability
                    break
            else:
                stable_count = 0
                last_length = current_length

        response = self.output_buffer.strip()
        self.output_buffer = ""
        return response

    def listen(self) -> str:
        """Listen for voice input."""
        self.listening = True
        print("\n🎤 Listening...")

        audio = self.recorder.record_until_silence(
            silence_threshold=0.01,
            silence_duration=1.2,
            max_duration=30.0,
        )

        self.listening = False
        print("🔄 Transcribing...")
        text = self.stt.transcribe(audio)
        return text.strip()

    async def speak(self, text: str):
        """Speak response."""
        # Clean up terminal escape codes
        import re
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        clean_text = re.sub(r'\x1b\[\?[0-9;]*[a-zA-Z]', '', clean_text)
        clean_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', clean_text)

        # Truncate for speech
        if len(clean_text) > 800:
            clean_text = clean_text[:800] + "... I've written more in the terminal."

        if clean_text.strip():
            await self.tts.speak_async(clean_text)

    async def run(self):
        """Run the interactive voice session."""
        print("\n" + "=" * 60)
        print("🎙️  Interactive Voice Claude")
        print("=" * 60)
        print("This is a CONTINUOUS conversation with Claude.")
        print("Speak naturally - context is preserved between messages.")
        print("Say 'exit' or 'goodbye' to end the session.")
        print("Press Ctrl+C to force quit.")
        print("=" * 60 + "\n")

        self.start_claude()

        await self.speak("I'm ready. What would you like to work on?")

        try:
            while True:
                # Listen for voice input
                text = self.listen()

                if not text:
                    print("(no speech detected)")
                    continue

                print(f"\n>>> You: {text}\n")

                # Check for exit
                if any(cmd in text.lower() for cmd in ["exit", "quit", "goodbye", "bye", "stop listening"]):
                    await self.speak("Goodbye! Ending the session.")
                    break

                # Send to Claude
                self.send_to_claude(text)

                # Wait for response
                response = self.wait_for_response()

                # Speak the response
                if response:
                    await self.speak(response)

        except KeyboardInterrupt:
            print("\n\nStopped by user.")
        finally:
            if self.claude_process:
                self.claude_process.terminate()
                self.claude_process.wait()

    def stop(self):
        """Stop the session."""
        if self.claude_process:
            self.claude_process.terminate()


def main():
    parser = argparse.ArgumentParser(description="Interactive voice interface for Claude Code")
    parser.add_argument("--cwd", type=str, default=None, help="Working directory")
    parser.add_argument("--model", type=str, default="base", help="Whisper model")

    args = parser.parse_args()

    voice = InteractiveVoiceClaude(cwd=args.cwd, model=args.model)
    asyncio.run(voice.run())


if __name__ == "__main__":
    main()
