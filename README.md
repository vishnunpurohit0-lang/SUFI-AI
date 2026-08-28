# Sufi — AI Voice Assistant

Sufi is a personal, offline-capable AI voice assistant built in Python. It listens for voice input, transcribes it locally using Whisper, sends it to an LLM for a response, and speaks the reply back — with support for system commands, memory, and a customizable identity/name.

> ⚠️ This project was previously named **Jarvis** during development. Some internal references may still use that name.

---

## ✨ Features

- 🎙️ **Voice input** — real-time microphone listening with energy-based voice activity detection (VAD)
- 🧠 **Speech-to-text** — local transcription via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (GPU-accelerated with CUDA)
- 🤖 **LLM-powered responses** — natural conversation handled through `brain/ai.py`
- 🗣️ **Text-to-speech** — spoken replies via `voice/speak.py`
- 🛠️ **System command execution** — run local OS-level commands via `tools/system_control.py`
- 🧾 **Memory** — short-term (`chat_memory.py`) and long-term (`long_term_memory.py`) conversation memory
- ✏️ **Dynamic identity** — rename the assistant on the fly with a spoken command (e.g. *"change your name to Sufi"*), persisted in `config.py` / `identity.json`

---

## 📂 Project Structure

```
sufi/
├── assets/                  # Static assets (images, audio, etc.)
├── brain/
│   └── ai.py                # LLM integration — generates responses
├── config.py                 # Assistant identity (name, wake words)
├── commands.py                # Local command handling (e.g. rename)
├── data/                      # Persistent data files
├── memory/
│   ├── chat_memory.py         # Short-term conversation memory
│   └── long_term_memory.py    # Long-term memory storage
├── tools/
│   └── system_control.py      # OS-level command execution
├── voice/
│   ├── assistant.py           # Main entry point / conversation loop
│   ├── listen.py               # Microphone capture + VAD + transcription
│   ├── speak.py                 # Text-to-speech output
│   └── vad.py                    # (reserved for future VAD logic)
├── requirements.txt
└── main.py                        # App launcher
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- A CUDA-capable GPU (recommended, for faster-whisper GPU inference) — CPU fallback also possible
- A working microphone

### Installation

```bash
git clone https://github.com/<your-username>/sufi.git
cd sufi

python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root with any required API keys (e.g. for your LLM provider):

```
OPENAI_API_KEY=your_key_here
```

> Adjust based on whichever LLM backend `brain/ai.py` calls.

### Running

```bash
python main.py
```

Say the assistant's wake word/name, speak your command, and Sufi will respond. Say **"exit"**, **"quit"**, or **"bye"** anytime to stop.

---

## 🔧 Configuration

The assistant's name and wake word live in `config.py`, backed by `identity.json` (auto-created on first run). You can:

- Say **"change your name to `<name>`"** while running, or
- Manually edit `identity.json`:

```json
{
  "name": "Sufi",
  "wake_words": ["sufi"]
}
```

---

## 🧩 Tech Stack

- **Language:** Python 3.12
- **Speech-to-text:** faster-whisper (Whisper, GPU/CUDA)
- **Audio I/O:** sounddevice, soundfile
- **Text-to-speech:** (fill in — e.g. pyttsx3 / edge-tts / ElevenLabs, whichever `speak.py` uses)
- **LLM backend:** (fill in — e.g. OpenAI / Anthropic / local model, whichever `brain/ai.py` calls)

---

## 📝 Notes

- `vad.py` is currently a placeholder — voice activity detection is handled inline in `listen.py`.
- This is an active work-in-progress personal project; expect breaking changes.

---

## 📄 License

(Add your license here — e.g. MIT, or "All rights reserved" if private.)
