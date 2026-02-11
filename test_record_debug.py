#!/usr/bin/env python3
"""Debug recording and transcription."""
import sys
sys.path.insert(0, "/Users/medisiva/Desktop/mycoding/voice-toolkit")

import numpy as np
import soundfile as sf
from voice_toolkit.stt import FasterWhisperSTT
from voice_toolkit.stt.whisper_stt import MicrophoneRecorder

print("Recording 5 seconds of audio...")
print("Say: 'Hello, my name is Siva'")
print()

recorder = MicrophoneRecorder()
audio = recorder.record(duration=5)

# Save to file
sf.write("debug_recording.wav", audio, 16000)
print(f"Saved to debug_recording.wav ({len(audio)} samples)")
print(f"Audio stats: min={audio.min():.4f}, max={audio.max():.4f}, mean={audio.mean():.4f}")

# Transcribe
print("\nTranscribing with small model...")
stt = FasterWhisperSTT(model="small")
text = stt.transcribe("debug_recording.wav", language="en")
print(f"Transcription: {text}")

print("\nPlaying back recording...")
import subprocess
subprocess.run(["afplay", "debug_recording.wav"])
print("Done. Did you hear your voice correctly?")
