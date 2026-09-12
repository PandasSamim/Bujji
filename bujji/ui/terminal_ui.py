"""
Terminal UI Presentation for Bujji using Rich.
Provides a modern, stylized, and scannable command-line experience.
"""

from typing import Any, Dict, List
import os
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown

console = Console()

BUJJI_BANNER = """
 ██████╗ ██╗   ██╗     ██╗     ██╗██╗
 ██╔══██╗██║   ██║     ██║     ██║██║
 ██████╔╝██║   ██║     ██║     ██║██║
 ██╔══██╗██║   ██║██   ██║██   ██║██║
 ██████╔╝╚██████╔╝╚█████╔╝╚█████╔╝██║
 ╚═════╝  ╚═════╝  ╚════╝  ╚════╝ ╚═╝
"""

def display_banner(assistant_name: str = "Bujji", version: str = "0.1.0", mode: str = "antigravity") -> None:
    """Display the introductory startup banner."""
    banner_text = Text(BUJJI_BANNER, style="bold cyan")
    subtitle = f"Personal AI Assistant | v{version} | Engine: [{mode.upper()}] | Inspired by JARVIS"
    
    panel = Panel(
        banner_text,
        title=f"[bold white]>>> {assistant_name.upper()} ONLINE <<<[/bold white]",
        subtitle=f"[dim]{subtitle}[/dim]",
        border_style="bright_blue",
        padding=(0, 2),
    )
    console.print(panel)
    console.print("[dim italic]Type your prompt, or use slash commands (/help, /status, /mode, /exit).[/dim italic]\n")

def display_status_table(status: Dict[str, Any]) -> None:
    """Display system status diagnostics in a clean table."""
    table = Table(title="[bold cyan]Bujji System Diagnostics[/bold cyan]", border_style="dim")
    table.add_column("Component", style="white")
    table.add_column("Status / Details", style="green")

    table.add_row("Assistant Name", status.get("name", "Bujji"))
    table.add_row("Active Engine Mode", f"[bold yellow]{status.get('mode', 'unknown')}[/bold yellow]")
    
    ag_installed = status.get("antigravity_sdk_installed", False)
    table.add_row("Antigravity SDK", "[green]Ready[/green]" if ag_installed else "[red]Missing[/red]")
    
    ollama_ready = status.get("ollama_connected", False)
    ollama_status = f"[green]Connected[/green] ({status.get('ollama_model', 'unknown')})" if ollama_ready else "[yellow]Disconnected (Start with 'ollama serve')[/yellow]"
    table.add_row("Ollama Tactical Core", ollama_status)
    
    table.add_row("Registered Tools", f"{status.get('tools_count', 0)} tools loaded")

    console.print(table)
    console.print()

def display_tools_table(schemas: List[Dict[str, Any]]) -> None:
    """Display all available tools and descriptions."""
    table = Table(title="[bold cyan]Registered Bujji Tools[/bold cyan]", border_style="dim")
    table.add_column("Tool Name", style="bold cyan")
    table.add_column("Description", style="white")

    for item in schemas:
        func = item.get("function", {})
        table.add_row(func.get("name", ""), func.get("description", ""))

    console.print(table)
    console.print()

if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def print_token(token: str) -> None:
    """Stream token to stdout safely across all Windows codepages."""
    try:
        sys.stdout.write(token)
        sys.stdout.flush()
    except UnicodeEncodeError:
        try:
            if hasattr(sys.stdout, "buffer"):
                sys.stdout.buffer.write(token.encode("utf-8", errors="replace"))
                sys.stdout.buffer.flush()
            else:
                sys.stdout.write(token.encode("ascii", errors="replace").decode("ascii"))
                sys.stdout.flush()
        except Exception:
            pass

def print_status_message(message: str) -> None:
    """Print an auxiliary status message or alert."""
    console.print(message)

def print_user_prompt_prefix() -> str:
    """Styled prompt symbol."""
    return "[bold green]Boss > [/bold green]"
