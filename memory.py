"""简单记忆系统"""

import json
from pathlib import Path
from datetime import datetime


class Memory:
    """基于文件的持久化记忆"""

    def __init__(self, memory_dir: str = ".ai-agent-memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.session_file = self.memory_dir / "current_session.json"
        self.history_file = self.memory_dir / "history.jsonl"
        self.notes_file = self.memory_dir / "notes.md"

    def save_session(self, messages: list):
        """保存当前会话"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "messages": messages[-20:],  # 只保留最近 20 条
        }
        self.session_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def load_session(self) -> list:
        """加载上次会话"""
        if not self.session_file.exists():
            return []
        try:
            data = json.loads(self.session_file.read_text())
            return data.get("messages", [])
        except Exception:
            return []

    def archive_session(self, messages: list):
        """归档会话到历史"""
        if not messages:
            return
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(messages),
            "preview": messages[0]["content"][:100] if messages else "",
        }
        with open(self.history_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def save_note(self, content: str):
        """保存笔记"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.notes_file, "a") as f:
            f.write(f"\n## {timestamp}\n{content}\n")

    def load_notes(self) -> str:
        """加载笔记"""
        if not self.notes_file.exists():
            return ""
        return self.notes_file.read_text(encoding="utf-8")

    def get_context(self) -> str:
        """获取记忆上下文（用于注入对话）"""
        notes = self.load_notes()
        if notes:
            return f"## 之前的笔记\n{notes[:1000]}"
        return ""
