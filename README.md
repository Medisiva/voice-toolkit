# Voice Toolkit

Modular STT/TTS library for building voice interfaces in Python.

## Features

- **Speech-to-Text (STT)**
  - Whisper (local, free, offline)
  - Microphone recording with silence detection

- **Text-to-Speech (TTS)**
  - Piper (local, free, offline)
  - Edge TTS (free, online, high quality)

- **Voice Assistant**
  - Combines STT + TTS for hands-free interaction
  - Optional wake word detection
  - Easy integration with any backend (LLMs, commands, etc.)

## Installation

```bash
# Install with all providers
pip install voice-toolkit[all]

# Or install specific providers
pip install voice-toolkit[whisper]  # STT only
pip install voice-toolkit[piper]    # Local TTS
pip install voice-toolkit[edge]     # Online TTS
```

## Quick Start

### Simple Voice Assistant

```python
from voice_toolkit import VoiceAssistant
from voice_toolkit.stt import WhisperSTT
from voice_toolkit.tts import PiperTTS

def process(text: str) -> str:
    return f"You said: {text}"

assistant = VoiceAssistant(
    stt=WhisperSTT(),
    tts=PiperTTS(),
    on_input=process,
)
assistant.start()
```

### STT Only

```python
from voice_toolkit.stt import WhisperSTT

stt = WhisperSTT(model="base")
text = stt.transcribe("audio.mp3")
print(text)
```

### TTS Only

```python
from voice_toolkit.tts import PiperTTS

tts = PiperTTS(voice="amy")
tts.speak("Hello, world!")  # Plays audio
tts.speak("Hello, world!", "output.wav")  # Saves to file
```

### With Claude/LLM

```python
from voice_toolkit import VoiceAssistant
from voice_toolkit.stt import WhisperSTT
from voice_toolkit.tts import EdgeTTS
import anthropic

client = anthropic.Anthropic()

def ask_claude(text: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].text

assistant = VoiceAssistant(
    stt=WhisperSTT(),
    tts=EdgeTTS(),
    on_input=ask_claude,
    wake_word="hey claude",
)
assistant.start()
```

## Available Voices

### Piper TTS (Local)
- `amy` - Female, American
- `ryan` - Male, American
- `jenny` - Female, British
- `danny` - Male, British

### Edge TTS (Online)
- `aria` - Female, conversational
- `guy` - Male, newscast
- `jenny` - Female, friendly
- `ana` - Female, child-like (great for kids content)

## Whisper Models

| Model  | Speed   | Accuracy | VRAM    |
|--------|---------|----------|---------|
| tiny   | Fastest | Basic    | ~1GB    |
| base   | Fast    | Good     | ~1GB    |
| small  | Medium  | Better   | ~2GB    |
| medium | Slow    | High     | ~5GB    |
| large  | Slowest | Best     | ~10GB   |

## API Reference

### WhisperSTT

```python
stt = WhisperSTT(
    model="base",           # Model size
    device=None,            # cuda/cpu/auto
    download_root=None,     # Model download directory
)

text = stt.transcribe(audio)           # File path or numpy array
text = stt.transcribe(audio, "en")     # With language hint
```

### PiperTTS

```python
tts = PiperTTS(
    voice="amy",            # Voice name or model ID
    speed=1.0,              # Speaking rate
)

tts.speak(text)                         # Play directly
tts.speak(text, "output.wav")           # Save to file
await tts.speak_async(text, "out.wav")  # Async
```

### EdgeTTS

```python
tts = EdgeTTS(
    voice="aria",           # Voice name
    rate="+0%",             # Speed adjustment
    pitch="+0Hz",           # Pitch adjustment
)

await tts.speak_async(text)             # Async (preferred)
tts.speak(text)                         # Sync wrapper
voices = await EdgeTTS.list_voices()    # List available voices
```

### VoiceAssistant

```python
assistant = VoiceAssistant(
    stt=stt,                        # STT provider
    tts=tts,                        # TTS provider
    on_input=callback,              # Function(text) -> response
    wake_word=None,                 # Optional activation phrase
    silence_threshold=0.01,         # Silence detection threshold
    silence_duration=1.5,           # Seconds of silence to stop
    max_listen_duration=30.0,       # Max recording time
)

assistant.start()                   # Blocking
assistant.start(blocking=False)     # Background thread
assistant.stop()                    # Stop listening
text = assistant.listen_once()      # Single utterance
assistant.say("Hello")              # Speak text
```

## License

MIT
