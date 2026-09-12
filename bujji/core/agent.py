"""
Bujji Agent Core Orchestrator.
Manages the agent lifecycle using Google Antigravity SDK with hybrid local Ollama fallback.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional
import asyncio
import os

from bujji.config import BujjiConfig
from bujji.core.prompts import get_system_instructions
from bujji.core.ollama_engine import OllamaEngine
from bujji.tools.registry import default_registry

try:
    from google.antigravity import Agent as AgAgent, LocalAgentConfig, CapabilitiesConfig
    ANTIGRAVITY_SDK_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_SDK_AVAILABLE = False

class BujjiAgent:
    """The central Bujji intelligence orchestrator."""

    def __init__(self, config: Optional[BujjiConfig] = None):
        self.config = config or BujjiConfig.load()
        self.name = self.config.assistant_name
        self.mode = self.config.default_engine  # 'antigravity', 'ollama', or 'hybrid'
        self.system_instructions = get_system_instructions(
            name=self.name,
            user_name=self.config.user_name,
            user_language=self.config.user_native_language,
        )
        
        # Setup Ollama fallback engine
        ollama_cfg = self.config.get("engine", {}).get("ollama", {})
        self.ollama = OllamaEngine(
            base_url=ollama_cfg.get("base_url", "http://localhost:11434"),
            model=ollama_cfg.get("model", "qwen2.5:7b"),
            temperature=ollama_cfg.get("temperature", 0.7),
        )

        # Conversation history for local modes
        self.history: List[Dict[str, str]] = []
        self._ag_agent = None

    def set_mode(self, new_mode: str) -> str:
        """Switch operational engine mode dynamically."""
        valid_modes = ["antigravity", "ollama", "hybrid"]
        if new_mode.lower() in valid_modes:
            self.mode = new_mode.lower()
            return f"Operational mode switched to: {self.mode}"
        return f"Invalid mode '{new_mode}'. Choose from: {', '.join(valid_modes)}"

    async def get_status(self) -> Dict[str, Any]:
        """Check status of primary and secondary engines."""
        ollama_ready = await self.ollama.is_available()
        return {
            "name": self.name,
            "mode": self.mode,
            "antigravity_sdk_installed": ANTIGRAVITY_SDK_AVAILABLE,
            "ollama_connected": ollama_ready,
            "ollama_model": self.ollama.model,
            "tools_count": len(default_registry.get_schemas()),
        }

    async def chat(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Sends a user prompt to the active engine and streams response events.
        Events are dicts: {"type": "token"|"thought"|"tool_call"|"status"|"error", ...}
        """
        self.history.append({"role": "user", "content": user_input})

        # Try Antigravity SDK if mode is 'antigravity' or 'hybrid' and API key is present
        api_key = os.getenv("GEMINI_API_KEY")
        if self.mode in ("antigravity", "hybrid") and ANTIGRAVITY_SDK_AVAILABLE and api_key:
            try:
                capabilities = CapabilitiesConfig()
                agent_config = LocalAgentConfig(
                    system_instructions=self.system_instructions,
                    capabilities=capabilities,
                )

                async with AgAgent(agent_config) as ag_instance:
                    response = await ag_instance.chat(user_input)
                    full_response = []

                    # Stream tokens
                    async for token in response:
                        full_response.append(token)
                        yield {"type": "token", "content": token}

                    assistant_text = "".join(full_response)
                    if assistant_text:
                        self.history.append({"role": "assistant", "content": assistant_text})
                    return

            except Exception as e:
                if self.mode == "antigravity":
                    yield {
                        "type": "error",
                        "content": f"Antigravity Engine Error: {e}\n(Tip: Switch to local engine using '/mode ollama' or '/mode hybrid')"
                    }
                    return
                else:
                    # In hybrid mode, notify fallback and continue with Ollama
                    yield {
                        "type": "status",
                        "content": f"[Yellow]Antigravity cloud uplink unavailable ({type(e).__name__}). Switching seamlessly to local tactical core (Ollama)...[/Yellow]"
                    }

        # Ollama local execution
        ollama_available = await self.ollama.is_available()
        if not ollama_available:
            yield {
                "type": "error",
                "content": (
                    f"No active engine available!\n"
                    f"- Antigravity SDK: { 'Failed' if ANTIGRAVITY_SDK_AVAILABLE else 'Not available' }\n"
                    f"- Ollama: Could not connect to {self.ollama.base_url}.\n"
                    f"Please verify GEMINI_API_KEY in .env or run 'ollama serve'."
                )
            }
            return

        full_response = []
        async for event in self.ollama.chat_stream(
            messages=self.history,
            system_prompt=self.system_instructions,
            use_tools=True
        ):
            if event["type"] == "token":
                full_response.append(event["content"])
                yield event
            elif event["type"] == "tool_call":
                # Execute tool via registry
                tool_name = event.get("name")
                args = event.get("arguments", {})
                yield {"type": "status", "content": f"[Cyan]Executing tool '{tool_name}'...[/Cyan]"}
                result = default_registry.execute(tool_name, args)
                # Feed tool result back to history
                self.history.append({
                    "role": "system",
                    "content": f"Tool '{tool_name}' executed. Result: {result}"
                })
                yield {"type": "tool_result", "name": tool_name, "result": result}
            else:
                yield event

        assistant_text = "".join(full_response)
        if assistant_text:
            self.history.append({"role": "assistant", "content": assistant_text})
