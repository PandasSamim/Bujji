"""
Terminal Execution Tool for Bujji.
Provides safe shell command execution with timeouts and destructive pattern rejection.
"""

from pathlib import Path
from typing import Any, Dict
import subprocess
import os
import shlex

WORKSPACE_ROOT = Path.cwd().resolve()

# Blacklist of catastrophic or dangerous commands
DANGEROUS_PATTERNS = [
    "format ",
    "rmdir /s",
    "rd /s",
    "del /s /q c:",
    "rm -rf /",
    ":(){ :|:& };:",
    "diskpart",
    "reg delete",
    "drop database",
]

def is_command_safe(command: str) -> tuple[bool, str]:
    """Check if the command contains any explicitly hazardous patterns."""
    lower_cmd = command.strip().lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in lower_cmd:
            return False, f"Command rejected: matches hazardous pattern '{pattern}'."
    return True, ""

def run_command(command: str, cwd: str = ".", timeout_seconds: int = 20) -> Dict[str, Any]:
    """
    Executes a shell command safely within the specified working directory.
    """
    safe, reason = is_command_safe(command)
    if not safe:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": reason,
            "command": command,
        }

    target_cwd = Path(cwd).resolve()
    if not target_cwd.exists() or not target_cwd.is_dir():
        target_cwd = WORKSPACE_ROOT

    try:
        # Use powershell on Windows, default shell otherwise
        shell_cmd = ["powershell", "-NoProfile", "-Command", command] if os.name == "nt" else command
        
        proc = subprocess.run(
            shell_cmd,
            cwd=str(target_cwd),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            encoding="utf-8",
            errors="replace"
        )
        return {
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "command": command,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout_seconds} seconds.",
            "command": command,
        }
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Execution error: {e}",
            "command": command,
        }
