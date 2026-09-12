"""
Bujji Core Agent Engine
Manages personality, reasoning loop, and model orchestrations (Antigravity SDK & Ollama).
"""

from bujji.core.prompts import get_system_instructions
from bujji.core.ollama_engine import OllamaEngine
from bujji.core.agent import BujjiAgent

__all__ = ["BujjiAgent", "OllamaEngine", "get_system_instructions"]
