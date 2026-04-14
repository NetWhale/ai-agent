"""配置管理"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # MiniMax API 配置
    API_KEY = os.getenv("MINIMAX_API_KEY", "")
    BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
    MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")

    # 对话配置
    MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))
    MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "4096"))

    # 系统提示词
    SYSTEM_PROMPT = """你是一个 AI 编程助手。
你的核心能力：
1. 理解和分析代码项目
2. 读写文件、执行命令
3. 帮助用户解决问题

行为准则：
- 直接回答，不废话
- 执行操作前先说明意图
- 遇到不确定的事主动确认
- 保持安全，拒绝危险操作

当需要使用工具时，使用以下格式：
```tool
{
  "name": "工具名",
  "args": { ... }
}
```

可用工具：
- read_file(path): 读取文件内容
- write_file(path, content): 写入文件
- exec_command(command): 执行 shell 命令
- list_files(path): 列出目录内容
- search_files(pattern, path): 搜索文件内容
"""

    @classmethod
    def validate(cls):
        if not cls.API_KEY:
            raise ValueError(
                "请在 .env 文件中设置 MINIMAX_API_KEY\n"
                "1. 复制 .env.example 为 .env\n"
                "2. 填入你的 MiniMax API Key"
            )
