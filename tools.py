"""工具系统"""

import os
import subprocess
from pathlib import Path
from safety import SafetyCheck
from rich.console import Console

console = Console()


class Tools:
    def __init__(self, work_dir: str = "."):
        self.work_dir = Path(work_dir).resolve()
        self.safety = SafetyCheck()

    def read_file(self, path: str) -> str:
        """读取文件内容"""
        safe, msg = self.safety.check_file_access(path)
        if not safe:
            return f"[安全拦截] {msg}"

        file_path = self.work_dir / path
        if not file_path.exists():
            return f"[错误] 文件不存在: {path}"
        if not file_path.is_file():
            return f"[错误] 不是文件: {path}"
        if file_path.stat().st_size > 1_000_000:
            return f"[错误] 文件过大 (>1MB): {path}"

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            if len(lines) > 200:
                content = "\n".join(lines[:200]) + f"\n... (共 {len(lines)} 行，已截断)"
            return f"📄 {path}:\n```\n{content}\n```"
        except UnicodeDecodeError:
            return f"[提示] 文件不是文本格式: {path}"

    def write_file(self, path: str, content: str) -> str:
        """写入文件"""
        safe, msg = self.safety.check_file_access(path)
        if not safe:
            return f"[安全拦截] {msg}"

        file_path = self.work_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            file_path.write_text(content, encoding="utf-8")
            return f"✅ 文件已写入: {path}"
        except Exception as e:
            return f"[错误] 写入失败: {e}"

    def exec_command(self, command: str) -> str:
        """执行 shell 命令"""
        safe, msg = self.safety.check_command(command)
        if not safe:
            return f"[安全拦截] {msg}"

        if self.safety.confirm_dangerous(command):
            console.print(f"\n⚠️  即将执行: [yellow]{command}[/yellow]")
            confirm = input("确认执行? (y/N): ").strip().lower()
            if confirm != "y":
                return "[已取消] 用户取消执行"

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.work_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n[返回码: {result.returncode}]"
            return output.strip() or "[命令执行完成，无输出]"
        except subprocess.TimeoutExpired:
            return "[错误] 命令执行超时 (30s)"
        except Exception as e:
            return f"[错误] 执行失败: {e}"

    def list_files(self, path: str = ".") -> str:
        """列出目录内容"""
        dir_path = self.work_dir / path
        if not dir_path.exists():
            return f"[错误] 目录不存在: {path}"
        if not dir_path.is_dir():
            return f"[错误] 不是目录: {path}"

        items = []
        for item in sorted(dir_path.iterdir()):
            prefix = "📁" if item.is_dir() else "📄"
            items.append(f"{prefix} {item.name}")

        if not items:
            return f"📂 {path}: (空目录)"
        return f"📂 {path}:\n" + "\n".join(items)

    def search_files(self, pattern: str, path: str = ".") -> str:
        """搜索文件内容"""
        search_path = self.work_dir / path
        if not search_path.exists():
            return f"[错误] 路径不存在: {path}"

        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.{py,js,ts,md,txt,json,yaml,yml,go,rs,java,c,cpp,h}",
                 pattern, str(search_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 50:
                    lines = lines[:50]
                    lines.append(f"... (共找到 {len(result.stdout.strip().split(chr(10)))} 条，已截断)")
                return "🔍 搜索结果:\n" + "\n".join(lines)
            return f"🔍 未找到匹配: {pattern}"
        except subprocess.TimeoutExpired:
            return "[错误] 搜索超时"
        except Exception:
            # fallback: 用 python 搜索
            matches = []
            for file_path in search_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in (".py", ".js", ".ts", ".md", ".txt", ".json"):
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        for i, line in enumerate(content.split("\n"), 1):
                            if pattern in line:
                                rel = file_path.relative_to(self.work_dir)
                                matches.append(f"{rel}:{i}: {line.strip()}")
                    except Exception:
                        continue
            if matches:
                return "🔍 搜索结果:\n" + "\n".join(matches[:50])
            return f"🔍 未找到匹配: {pattern}"

    def execute_tool(self, tool_name: str, args: dict) -> str:
        """统一工具执行入口"""
        tool_map = {
            "read_file": lambda: self.read_file(args.get("path", "")),
            "write_file": lambda: self.write_file(args.get("path", ""), args.get("content", "")),
            "exec_command": lambda: self.exec_command(args.get("command", "")),
            "list_files": lambda: self.list_files(args.get("path", ".")),
            "search_files": lambda: self.search_files(args.get("pattern", ""), args.get("path", ".")),
        }

        if tool_name not in tool_map:
            return f"[错误] 未知工具: {tool_name}"

        return tool_map[tool_name]()
