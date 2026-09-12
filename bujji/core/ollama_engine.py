"""
Ollama Engine Integration for Bujji.
Provides local, private, and offline LLM reasoning with streaming and tool calling support.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional
import json
import httpx

from bujji.tools.registry import default_registry

class OllamaEngine:
    """Local LLM engine interfacing with Ollama's REST API."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b",
        temperature: float = 0.7,
        timeout_seconds: float = 60.0
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout_seconds

    async def is_available(self) -> bool:
        """Checks if the Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def get_available_models(self) -> List[str]:
        """Fetch list of models locally pulled in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        use_tools: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams chat completion tokens from Ollama.
        Yields dictionaries with type: 'token', 'thought', 'tool_call', or 'done'.
        """
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        # Auto-detect available local model if configured model is not found
        available = await self.get_available_models()
        if available and not any(self.model in m for m in available):
            self.model = available[0]

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": payload_messages,
            "stream": True,
            "options": {
                "temperature": self.temperature,
            }
        }

        if use_tools:
            schemas = default_registry.get_schemas()
            if schemas:
                payload["tools"] = schemas

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    if response.status_code != 200:
                        yield {
                            "type": "error",
                            "content": f"Ollama HTTP error {response.status_code}: {await response.aread()}"
                        }
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            msg = chunk.get("message", {})
                            content = msg.get("content", "")
                            
                            # Handle tool calls if returned by model
                            tool_calls = msg.get("tool_calls", [])
                            if tool_calls:
                                for tc in tool_calls:
                                    func_info = tc.get("function", {})
                                    name = func_info.get("name")
                                    args = func_info.get("arguments", {})
                                    yield {
                                        "type": "tool_call",
                                        "name": name,
                                        "arguments": args
                                    }
                            
                            if content:
                                yield {
                                    "type": "token",
                                    "content": content
                                }
                                
                            if chunk.get("done", False):
                                yield {"type": "done"}
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            yield {
                "type": "error",
                "content": f"Could not connect to Ollama at {self.base_url}. Ensure Ollama is running."
            }
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Ollama generation error: {e}"
            }
