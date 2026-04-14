"""AI Agent - CLI 交互式 AI 助手"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from agent import Agent
from config import Config

console = Console()

BANNER = """
╔══════════════════════════════════════╗
║        🤖 AI Agent v0.1             ║
║    CLI 智能助手 (MiniMax)           ║
╚══════════════════════════════════════╝
"""

HELP_TEXT = """
[bold]内置命令:[/bold]
  /help     - 显示帮助
  /reset    - 重置会话
  /context  - 显示项目上下文
  /notes    - 显示笔记
  /clear    - 清屏
  /quit     - 退出
"""


@click.command()
@click.option("-d", "--dir", default=".", help="工作目录")
@click.option("--reset", is_flag=True, help="启动时重置会话")
def main(dir: str, reset: bool):
    """AI Agent - CLI 交互式 AI 助手"""
    console.print(Panel(BANNER, border_style="cyan"))

    try:
        agent = Agent(work_dir=dir)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    if reset:
        agent.reset()

    agent.init_messages()

    # 显示项目类型
    project_type = agent.context.detect_project_type()
    console.print(f"📂 工作目录: [cyan]{dir}[/cyan]")
    console.print(f"📦 项目类型: [cyan]{project_type}[/cyan]")
    console.print(f"🤖 模型: [cyan]{Config.MODEL}[/cyan]")
    console.print()

    # 交互主循环
    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")

            if not user_input.strip():
                continue

            # 处理内置命令
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()
                if cmd in ("/quit", "/exit", "/q"):
                    agent.memory.archive_session(agent.messages)
                    console.print("[dim]再见! 👋[/dim]")
                    break
                elif cmd == "/help":
                    console.print(Panel(HELP_TEXT, title="帮助", border_style="yellow"))
                elif cmd == "/reset":
                    agent.reset()
                elif cmd == "/context":
                    ctx = agent.context.get_context_summary()
                    console.print(Panel(ctx, title="项目上下文", border_style="blue"))
                elif cmd == "/notes":
                    notes = agent.memory.load_notes()
                    if notes:
                        console.print(Panel(notes, title="笔记", border_style="magenta"))
                    else:
                        console.print("[dim]暂无笔记[/dim]")
                elif cmd == "/clear":
                    console.clear()
                else:
                    console.print(f"[red]未知命令: {cmd}[/red]")
                    console.print(HELP_TEXT)
                continue

            # 普通对话
            agent.chat(user_input)

        except KeyboardInterrupt:
            console.print("\n[dim]使用 /quit 退出[/dim]")
        except EOFError:
            break


if __name__ == "__main__":
    main()
