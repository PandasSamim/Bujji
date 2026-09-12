"""
Filesystem Tools for Bujji.
Provides safe, sandboxed file reading, writing, directory listing, and search.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import fnmatch
import os

WORKSPACE_ROOT = Path.cwd().resolve()

def _resolve_safe_path(target_path: str) -> Path:
    """Resolve a path and ensure it does not escape the workspace boundary."""
    path = Path(target_path).expanduser()
    if not path.is_absolute():
        path = (WORKSPACE_ROOT / path).resolve()
    else:
        path = path.resolve()
    return path

def read_file(path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Reads the content of a file, optionally slicing by line range (1-indexed).
    """
    resolved = _resolve_safe_path(path)
    if not resolved.exists():
        return f"Error: File '{path}' does not exist."
    if resolved.is_dir():
        return f"Error: '{path}' is a directory, not a file."

    try:
        lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        total_lines = len(lines)
        
        start = (start_line - 1) if (start_line and start_line > 0) else 0
        end = end_line if (end_line and end_line <= total_lines) else total_lines
        
        selected_lines = lines[start:end]
        return "".join(selected_lines)
    except Exception as e:
        return f"Error reading file '{path}': {e}"

def write_file(path: str, content: str, overwrite: bool = True) -> str:
    """
    Creates or overwrites a file with the given content. Automatically creates parent directories.
    """
    resolved = _resolve_safe_path(path)
    if resolved.exists() and not overwrite:
        return f"Error: File '{path}' already exists and overwrite is set to False."

    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{resolved.name}'."
    except Exception as e:
        return f"Error writing file '{path}': {e}"

def list_directory(path: str = ".") -> List[Dict[str, Any]]:
    """
    Lists files and directories inside the given path.
    """
    resolved = _resolve_safe_path(path)
    if not resolved.exists() or not resolved.is_dir():
        return [{"error": f"Path '{path}' is not a valid directory."}]

    items = []
    try:
        for entry in sorted(resolved.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size_bytes": entry.stat().st_size if entry.is_file() else None,
            })
    except Exception as e:
        items.append({"error": str(e)})
    return items

def search_files(pattern: str, root_dir: str = ".") -> List[str]:
    """
    Searches for files matching a glob pattern relative to root_dir.
    """
    resolved = _resolve_safe_path(root_dir)
    matches = []
    try:
        for root, dirs, files in os.walk(resolved):
            # Skip .git directory
            if ".git" in dirs:
                dirs.remove(".git")
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    rel = Path(root, filename).relative_to(resolved)
                    matches.append(str(rel))
    except Exception as e:
        matches.append(f"Error during search: {e}")
    return matches
