"""Voice Assistant - combines STT and TTS for voice interaction."""

import asyncio
import threading
from typing import Callable, Optional

from ..stt.base import BaseSTT
from ..tts.base import BaseTTS


class VoiceAssistant:
    """
    Voice Assistant that combines STT and TTS for hands-free interaction.

    Usage:
        from voice_toolkit import VoiceAssistant
        from voice_toolkit.stt import WhisperSTT
        from voice_toolkit.tts import PiperTTS

        def process(text: str) -> str:
            # Your logic here - could call an LLM, run commands, etc.
            return f"You said: {text}"

        assistant = VoiceAssistant(
            stt=WhisperSTT(),
            tts=PiperTTS(),
            on_input=process,
        )
        assistant.start()  # Blocking - listens and responds
    """

    def __init__(
        self,
        stt: BaseSTT,
        tts: BaseTTS,
        on_input: Callable[[str], str],
        wake_word: Optional[str] = None,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,
        max_listen_duration: float = 30.0,
    ):
        """
        Initialize Voice Assistant.

        Args:
            stt: Speech-to-Text provider
            tts: Text-to-Speech provider
            on_input: Callback function that receives transcribed text
                     and returns response text to speak
            wake_word: Optional wake word to trigger listening (e.g., "hey claude")
            silence_threshold: RMS threshold for silence detection
            silence_duration: Seconds of silence to stop listening
            max_listen_duration: Maximum listening time in seconds
        """
        self.stt = stt
        self.tts = tts
        self.on_input = on_input
        self.wake_word = wake_word.lower() if wake_word else None
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_listen_duration = max_listen_duration

        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self, blocking: bool = True) -> None:
        """
        Start the voice assistant.

        Args:
            blocking: If True, blocks until stop() is called.
                     If False, runs in background thread.
        """
        self._running = True

        if blocking:
            self._run_loop()
        else:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stop the voice assistant."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run_loop(self) -> None:
        """Main listening loop."""
        from ..stt.whisper_stt import MicrophoneRecorder

        recorder = MicrophoneRecorder()

        print("Voice Assistant started. Listening...")
        if self.wake_word:
            print(f"Say '{self.wake_word}' to activate.")

        while self._running:
            try:
                # Record audio
                audio = recorder.record_until_silence(
                    silence_threshold=self.silence_threshold,
                    silence_duration=self.silence_duration,
                    max_duration=self.max_listen_duration,
                )

                # Transcribe
                text = self.stt.transcribe(audio)
                if not text.strip():
                    continue

                print(f"Heard: {text}")

                # Check wake word if configured
                if self.wake_word:
                    if self.wake_word not in text.lower():
                        continue
                    # Remove wake word from text
                    text = text.lower().replace(self.wake_word, "").strip()

                # Process input and get response
                response = self.on_input(text)

                if response:
                    print(f"Response: {response}")
                    self.tts.speak(response)

            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")

        self._running = False
        print("Voice Assistant stopped.")

    def listen_once(self) -> str:
        """
        Listen for a single utterance and return transcribed text.

        Returns:
            Transcribed text
        """
        from ..stt.whisper_stt import MicrophoneRecorder

        recorder = MicrophoneRecorder()
        audio = recorder.record_until_silence(
            silence_threshold=self.silence_threshold,
            silence_duration=self.silence_duration,
            max_duration=self.max_listen_duration,
        )
        return self.stt.transcribe(audio)

    def say(self, text: str) -> None:
        """
        Speak the given text.

        Args:
            text: Text to speak
        """
        self.tts.speak(text)

    async def listen_once_async(self) -> str:
        """
        Listen for a single utterance asynchronously.

        Returns:
            Transcribed text
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.listen_once)

    async def say_async(self, text: str) -> None:
        """
        Speak the given text asynchronously.

        Args:
            text: Text to speak
        """
        await self.tts.speak_async(text)
