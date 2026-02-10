#!/usr/bin/env python3
"""Test microphone levels to find the right silence threshold."""

import sys
sys.path.insert(0, "/Users/medisiva/Desktop/mycoding/voice-toolkit")

import numpy as np
import sounddevice as sd

print("=" * 50)
print("Microphone Level Test")
print("=" * 50)
print("Speak into your microphone. Watch the levels.")
print("Press Ctrl+C to stop.")
print("=" * 50)

sample_rate = 16000
chunk_duration = 0.1
chunk_samples = int(chunk_duration * sample_rate)

try:
    while True:
        audio = sd.rec(chunk_samples, samplerate=sample_rate, channels=1, dtype=np.float32)
        sd.wait()
        
        rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        
        # Visual bar
        bar_length = int(rms * 500)
        bar = "█" * min(bar_length, 50)
        
        status = "SPEECH" if rms > 0.01 else "silence"
        print(f"RMS: {rms:.4f} | Peak: {peak:.4f} | {bar:<50} | {status}")
        
except KeyboardInterrupt:
    print("\n\nDone! Use a silence_threshold slightly below your quiet RMS level.")
