"""项目上下文感知"""

import os
from pathlib import Path


class Context:
    """自动感知项目结构和关键文件"""

    IGNORE_DIRS = {
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", "target", ".idea", ".vscode",
    }

    def __init__(self, work_dir: str = "."):
        self.work_dir = Path(work_dir).resolve()

    def get_project_tree(self, max_depth: int = 3) -> str:
        """获取项目目录树"""
        lines = []

        def walk(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            if path.name.startswith(".") and path.name not in (".env", ".gitignore"):
                return
            if path.name in self.IGNORE_DIRS:
                return

            try:
                entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            except PermissionError:
                return

            dirs = [e for e in entries if e.is_dir() and e.name not in self.IGNORE_DIRS]
            files = [e for e in entries if e.is_file()]

            for i, d in enumerate(dirs):
                is_last = (i == len(dirs) - 1) and len(files) == 0
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{d.name}/")
                extension = "    " if is_last else "│   "
                walk(d, prefix + extension, depth + 1)

            for i, f in enumerate(files):
                is_last = i == len(files) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{f.name}")

        lines.append(f"{self.work_dir.name}/")
        walk(self.work_dir)
        return "\n".join(lines)

    def detect_project_type(self) -> str:
        """检测项目类型"""
        indicators = {
            "package.json": "Node.js",
            "requirements.txt": "Python",
            "pyproject.toml": "Python",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java (Gradle)",
            "Gemfile": "Ruby",
            "composer.json": "PHP",
            "*.csproj": ".NET",
            "Makefile": "C/C++",
            "CMakeLists.txt": "C/C++ (CMake)",
        }

        for indicator, project_type in indicators.items():
            if "*" in indicator:
                if list(self.work_dir.glob(indicator)):
                    return project_type
            elif (self.work_dir / indicator).exists():
                return project_type

        return "未知"

    def get_key_files(self) -> dict:
        """读取关键配置文件"""
        key_files = {}
        candidates = [
            "README.md", "README.rst",
            "package.json", "pyproject.toml", "requirements.txt",
            "Cargo.toml", "go.mod",
            "Makefile", "Dockerfile", "docker-compose.yml",
            ".gitignore",
        ]

        for name in candidates:
            path = self.work_dir / name
            if path.exists() and path.stat().st_size < 10000:
                try:
                    key_files[name] = path.read_text(encoding="utf-8")[:2000]
                except Exception:
                    continue

        return key_files

    def get_context_summary(self) -> str:
        """生成项目上下文摘要"""
        project_type = self.detect_project_type()
        tree = self.get_project_tree()
        key_files = self.get_key_files()

        summary = f"""## 项目信息
- 类型: {project_type}
- 路径: {self.work_dir}

## 目录结构
```
{tree}
```
"""

        if key_files:
            summary += "\n## 关键文件\n"
            for name, content in key_files.items():
                summary += f"\n### {name}\n```\n{content[:500]}\n```\n"

        return summary
