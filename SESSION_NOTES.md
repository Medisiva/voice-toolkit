# Voice Toolkit Session Notes - 2026-02-10

## What We Built

### voice-toolkit repo
GitHub: https://github.com/Medisiva/voice-toolkit

**STT (Speech-to-Text):**
- `WhisperSTT` - Original Whisper (has Python 3.12 issues)
- `FasterWhisperSTT` - Recommended, works on Python 3.12
- `MicrophoneRecorder` - Records with silence detection

**TTS (Text-to-Speech):**
- `PiperTTS` - Local, free, offline
- `EdgeTTS` - Microsoft Edge, free, online, high quality

**Integrations:**
- `voice_claude.py` - Basic voice → Claude Code (one-shot)
- `voice_claude_interactive.py` - Interactive pty session (had issues)
- `voice_claude_simple.py` - Uses `claude -p --continue`
- `web_voice/` - Browser-based with Web Speech API (WORKS BEST)

## What Works

1. **Web Voice Interface** (Best option currently)
   ```bash
   cd /Users/medisiva/Desktop/mycoding/voice-toolkit
   python3 web_voice/server.py
   # Open http://localhost:8096 in Chrome
   ```

2. **macOS Dictation** (User testing this)
   - System Settings → Keyboard → Dictation → On
   - Press Fn twice to dictate

## Next Steps

1. **VoiceMode MCP** - Installed but skill not working
   - `voice-mode` package installed via pip3
   - Need to add as MCP server: `claude mcp add voicemode`

2. **Remote/Mobile Access**
   - Expose web_voice via Cloudflare Tunnel
   - Or use LiveKit for real-time streaming

## Key Findings

- Whisper `base` model had poor accuracy
- Whisper `small` model better but still issues
- **Chrome Web Speech API** has best accuracy
- macOS dictation could be simplest solution

## Commands Reference

```bash
# Test microphone levels
cd /Users/medisiva/Desktop/mycoding/voice-toolkit
.venv/bin/python test_mic_level.py

# Test recording + transcription
.venv/bin/python test_record_debug.py

# Web voice server
python3 web_voice/server.py

# VoiceMode (needs setup)
claude mcp add --scope user voicemode -- python3 -m voice_mode
```
