# Bujji - Project Architecture & Roadmap

> **Bujji** is an autonomous personal AI assistant inspired by JARVIS, designed for 100% free local & offline operation via Ollama (`qwen2.5:7b`) with zero API costs, hybrid cloud support, voice interaction, system control, persistent memory, and an overlay UI.
> 
> **GitHub Repository**: [PandasSamim/Bujji](https://github.com/PandasSamim/Bujji) (Branch: `main`)

---

## 1. Clean Project Structure

```
Bujji/
├── .antigravity/               # Isolated testing files, verification scripts, helper tools, scratch (git-ignored)
│   ├── README.md               # Folder purpose & usage guide
│   └── test_sdk.py             # Environment & SDK verification script
├── .env.example                # Sample environment configuration
├── .gitignore                  # Git exclusion rules (.antigravity/, .env, venvs, cache)
├── config.yaml                 # Core configuration (personality, engines, voice, tools)
├── handoff.md                  # Operational status, accomplishments, and handoff log
├── outline.md                  # Architecture overview & multi-phase roadmap (this document)
├── requirements.txt            # Python dependencies (google-antigravity, rich, pyyaml, etc.)
├── rules.md                    # Mandatory operating rules and quality constraints
└── bujji/                      # Main source package
    ├── __init__.py             # Package metadata
    ├── config.py               # Configuration loader & validator
    ├── core/                   # Phase 2: Core Agent Engine
    │   ├── __init__.py
    │   ├── agent.py            # Primary agent orchestrator (Antigravity SDK + Ollama hybrid)
    │   └── prompts.py          # Personality, system instructions & formatting rules
    ├── tools/                  # Phase 2 & 4: Tools Framework
    │   ├── __init__.py         # Tool registry and dispatch
    │   ├── filesystem.py       # File reading, writing, search
    │   ├── terminal.py         # Safe command runner
    │   └── web.py              # Web search and URL fetching
    ├── voice/                  # Phase 3: Voice Subsystem
    │   ├── __init__.py
    │   ├── wakeword.py         # Wake word detection ("Hey Bujji")
    │   ├── stt.py              # Speech-to-Text (faster-whisper)
    │   ├── tts.py              # Text-to-Speech (Piper TTS)
    │   └── loop.py             # Voice state loop (Listening / Thinking / Speaking)
    ├── system/                 # Phase 4: System Control
    │   ├── __init__.py
    │   ├── apps.py             # App launching & process management
    │   ├── input.py            # Mouse & keyboard automation
    │   ├── screen.py           # Screenshot capture & vision understanding
    │   └── safety.py           # Confirmation guards for critical actions
    ├── memory/                 # Phase 5: Memory Management
    │   ├── __init__.py
    │   ├── conversation.py     # Short-term chat history
    │   ├── vector_store.py     # ChromaDB semantic memory store
    │   └── user_profile.py     # Long-term user preferences & facts
    └── ui/                     # Phase 6: User Interface
        ├── __init__.py
        ├── terminal_ui.py      # Rich terminal display
        └── overlay.py          # Floating UI / Status overlay
```

---

## 2. Multi-Phase Roadmap

### Phase 1: Foundation [COMPLETED]
- [x] Create clean project structure and package folders (`bujji/`).
- [x] Create `.antigravity/` folder and add to `.gitignore`.
- [x] Maintain living markdown files: [`rules.md`](file:///c:/Users/asami/DOCS/Bujji/rules.md), [`outline.md`](file:///c:/Users/asami/DOCS/Bujji/outline.md), [`handoff.md`](file:///c:/Users/asami/DOCS/Bujji/handoff.md).
- [x] Initialize Git repository with clean commits.
- [x] Setup basic configuration (`config.yaml`, `.env.example`, [`bujji/config.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/config.py)).
- [x] Setup `requirements.txt`.
- [x] Install & verify Antigravity SDK (`google-antigravity`) with test script in `.antigravity/`.

### Phase 2: Core Agent [COMPLETED]
- **Step 2.1: Personality & System Prompt Architecture**
  - [x] Implement [`bujji/core/prompts.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/core/prompts.py): JARVIS-inspired identity (confident, polite, witty, proactive, concise).
  - [x] Define formatting protocols, tool execution awareness, and safety guidelines in system instructions.
- **Step 2.2: Tooling Framework & Execution Handlers**
  - [x] Implement [`bujji/tools/filesystem.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/tools/filesystem.py): Safe read, write, list, and search within project boundaries.
  - [x] Implement [`bujji/tools/terminal.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/tools/terminal.py): Safe terminal command execution with timeouts and blocked dangerous patterns.
  - [x] Implement [`bujji/tools/registry.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/tools/registry.py): Central tool dispatcher with unified schema for both Antigravity and Ollama.
- **Step 2.3: Hybrid Model Engine (Antigravity SDK + Ollama)**
  - [x] Implement [`bujji/core/agent.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/core/agent.py): Unified `BujjiAgent` orchestrator managing life-cycle, model switching, and session state.
  - [x] Implement [`bujji/core/ollama_engine.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/core/ollama_engine.py): Local LLM fallback engine via Ollama REST/API client for offline resilience.
  - [x] Implement intelligent failover: Antigravity primary -> Ollama local fallback -> graceful error recovery.
- **Step 2.4: Interactive Text Chat Loop & Terminal UI**
  - [x] Implement [`bujji/ui/terminal_ui.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/ui/terminal_ui.py): Rich terminal presentation with Bujji banner, status indicators, and streaming tokens.
  - [x] Implement [`bujji/main.py`](file:///c:/Users/asami/DOCS/Bujji/bujji/main.py): Interactive CLI entry point with commands (`/mode`, `/status`, `/tools`, `/exit`).
- **Step 2.5: Verification & Test Suite in `.antigravity/`**
  - [x] Create [`.antigravity/test_phase2_agent.py`](file:///c:/Users/asami/DOCS/Bujji/.antigravity/test_phase2_agent.py): Verify prompt building, tool execution, failover routing, and streaming output.
  - [x] Create [`.antigravity/test_cli_commands.py`](file:///c:/Users/asami/DOCS/Bujji/.antigravity/test_cli_commands.py): Verify slash commands and system diagnostics.
  - [x] Execute tests and verify zero main-project contamination.

### Phase 3: Voice System
- [ ] Wake word detection ("Hey Bujji") using openwake-word or Porcupine.
- [ ] Speech-to-Text (STT) via `faster-whisper`.
- [ ] Text-to-Speech (TTS) using local high-performance Piper TTS.
- [ ] Complete voice loop with clear state transitions: `[Listening] -> [Thinking] -> [Speaking]`.

### Phase 4: System Control
- [ ] Application lifecycle control (launching, closing, switching apps).
- [ ] Mouse and keyboard automation via `pyautogui`.
- [ ] Screenshot capture and screen comprehension.
- [ ] File operations and web search integration.
- [ ] Mandatory safety confirmation protocol for destructive or sensitive system actions.

### Phase 5: Memory Subsystem
- [ ] Rolling conversation history and context window pruning.
- [ ] Vector memory integration using ChromaDB for long-term document & memory recall.
- [ ] Persistent user profile and preferences management.

### Phase 6: Advanced Features
- [ ] Multi-step autonomous task planning and execution.
- [ ] Sub-agent delegation for concurrent or specialized jobs.
- [ ] Lightweight floating UI / status overlay widget.
- [ ] Robust error handling, auto-recovery, and cross-platform compatibility.

### Phase 7: Polish & Delivery
- [ ] Complete, professional `README.md` with setup guides and architecture documentation.
- [ ] End-to-end integration testing across all subsystems (inside `.antigravity/`).
- [ ] Performance profiling, memory footprint optimization, and codebase cleanup.
