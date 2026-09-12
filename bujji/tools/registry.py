"""
Central Tool Registry and Dispatcher for Bujji.
Maintains tool schemas and dispatches function calls for both Antigravity and Ollama.
"""

from typing import Any, Callable, Dict, List, Optional
import inspect
import json

from bujji.tools.filesystem import read_file, write_file, list_directory, search_files
from bujji.tools.terminal import run_command

class ToolRegistry:
    """Manages tool registration, metadata schemas, and dynamic invocation."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register(self, name: str, func: Callable, description: str, parameters: Dict[str, Any]) -> None:
        """Register a function with its JSON schema definition."""
        self._tools[name] = func
        self._schemas[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        }

    def _register_default_tools(self) -> None:
        """Register the core toolset for Phase 2."""
        self.register(
            name="read_file",
            func=read_file,
            description="Reads file contents with optional 1-indexed line range slicing.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative or absolute path of the file to read."},
                    "start_line": {"type": "integer", "description": "Optional starting line number (1-indexed)."},
                    "end_line": {"type": "integer", "description": "Optional ending line number (inclusive)."},
                },
                "required": ["path"],
            },
        )

        self.register(
            name="write_file",
            func=write_file,
            description="Writes or overwrites content to a specified file, creating directories as needed.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Target file path."},
                    "content": {"type": "string", "description": "Complete text content to write."},
                    "overwrite": {"type": "boolean", "description": "Whether to overwrite existing file. Defaults to true."},
                },
                "required": ["path", "content"],
            },
        )

        self.register(
            name="list_directory",
            func=list_directory,
            description="Lists all files and folders located within a directory path.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list. Defaults to current directory '.'"},
                },
            },
        )

        self.register(
            name="search_files",
            func=search_files,
            description="Searches for files matching a wildcard glob pattern within the workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "File pattern to match, e.g. '*.py' or '*config*'"},
                    "root_dir": {"type": "string", "description": "Root directory to search in. Defaults to '.'"},
                },
                "required": ["pattern"],
            },
        )

        self.register(
            name="run_command",
            func=run_command,
            description="Executes a shell command safely, returning stdout, stderr, and exit code.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command line string to run."},
                    "cwd": {"type": "string", "description": "Current working directory. Defaults to '.'"},
                    "timeout_seconds": {"type": "integer", "description": "Timeout in seconds. Defaults to 20."},
                },
                "required": ["command"],
            },
        )

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Return all tool schemas in standard function-calling format."""
        return list(self._schemas.values())

    def execute(self, tool_name: str, arguments: Dict[str, Any] | str) -> Any:
        """Execute a registered tool by name with arguments."""
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' is not registered."

        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except Exception as e:
                return f"Error: Failed to parse tool arguments JSON: {e}"

        func = self._tools[tool_name]
        try:
            return func(**arguments)
        except Exception as e:
            return f"Error invoking tool '{tool_name}': {e}"

# Global registry instance
default_registry = ToolRegistry()
