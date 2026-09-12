"""
Bujji Main CLI Entry Point.
Runs the interactive chat loop with rich styling and slash command controls.
"""

from typing import Optional
from pathlib import Path
import asyncio
import sys
import os

# Ensure project root is on sys.path when executed directly as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure Windows terminal handles UTF-8 safely
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from bujji.config import BujjiConfig
from bujji.core.agent import BujjiAgent
from bujji.tools.registry import default_registry
from bujji.ui.terminal_ui import (
    console,
    display_banner,
    display_status_table,
    display_tools_table,
    print_token,
    print_status_message,
)

async def handle_slash_command(command_str: str, agent: BujjiAgent) -> bool:
    """
    Handles slash commands. Returns True if the session should continue, False to exit.
    """
    parts = command_str.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in ("/exit", "/quit", "exit", "quit"):
        console.print("\n[bold cyan]Bujji:[/bold cyan] [italic]Powering down tactical interface. At your service whenever you need me, boss.[/italic]\n")
        return False

    elif cmd in ("/help", "/?"):
        console.print("""
[bold cyan]Available Commands:[/bold cyan]
  [green]/status[/green]             - View current engine state and loaded tools
  [green]/mode <engine>[/green]     - Switch engine: [bold]antigravity[/bold], [bold]ollama[/bold], or [bold]hybrid[/bold]
  [green]/tools[/green]              - View registered tools and capabilities
  [green]/clear[/green]              - Clear the terminal screen
  [green]/help[/green]               - Show this help menu
  [green]/exit[/green]               - Terminate the session
""")
        return True

    elif cmd == "/status":
        status = await agent.get_status()
        display_status_table(status)
        return True

    elif cmd == "/tools":
        schemas = default_registry.get_schemas()
        display_tools_table(schemas)
        return True

    elif cmd == "/mode":
        if not arg:
            console.print(f"[yellow]Current mode is: {agent.mode}. Usage: /mode <antigravity|ollama|hybrid>[/yellow]")
        else:
            msg = agent.set_mode(arg)
            console.print(f"[green]{msg}[/green]")
        return True

    elif cmd == "/clear":
        os.system("cls" if os.name == "nt" else "clear")
        display_banner(agent.name, agent.config.assistant_version, agent.mode)
        return True

    else:
        console.print(f"[yellow]Unrecognized command '{cmd}'. Type /help for available options.[/yellow]")
        return True

async def run_chat_loop(agent: BujjiAgent) -> None:
    """Runs the asynchronous interactive terminal loop."""
    display_banner(agent.name, agent.config.assistant_version, agent.mode)

    while True:
        try:
            user_input = console.input("[bold green]Boss > [/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session interrupted. Exiting...[/dim]")
            break

        if not user_input:
            continue

        if user_input.startswith("/") or user_input.lower() in ("exit", "quit"):
            should_continue = await handle_slash_command(user_input, agent)
            if not should_continue:
                break
            continue

        # Normal prompt to Bujji
        console.print(f"\n[bold cyan]{agent.name} > [/bold cyan]", end="")
        
        try:
            async for event in agent.chat(user_input):
                event_type = event.get("type")
                if event_type == "token":
                    print_token(event.get("content", ""))
                elif event_type == "status":
                    console.print(f"\n{event.get('content', '')}")
                elif event_type == "tool_result":
                    pass
                elif event_type == "error":
                    console.print(f"\n[bold red]Error:[/bold red] {event.get('content', '')}")
            console.print("\n")
        except Exception as e:
            console.print(f"\n[bold red]Unexpected Error:[/bold red] {e}\n")

def main():
    """CLI entrypoint."""
    cfg = BujjiConfig.load()
    agent = BujjiAgent(cfg)
    try:
        asyncio.run(run_chat_loop(agent))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
