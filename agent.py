"""核心 Agent 逻辑"""

import json
import re
from openai import OpenAI
from config import Config
from tools import Tools
from context import Context
from memory import Memory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

console = Console()


class Agent:
    def __init__(self, work_dir: str = "."):
        Config.validate()
        self.client = OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL,
        )
        self.tools = Tools(work_dir)
        self.context = Context(work_dir)
        self.memory = Memory()
        self.messages = []
        self.work_dir = work_dir

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        prompt = Config.SYSTEM_PROMPT

        # 注入项目上下文
        ctx = self.context.get_context_summary()
        prompt += f"\n\n{ctx}"

        # 注入记忆
        memory_ctx = self.memory.get_context()
        if memory_ctx:
            prompt += f"\n\n{memory_ctx}"

        return prompt

    def init_messages(self):
        """初始化消息列表"""
        # 尝试加载上次会话
        saved = self.memory.load_session()
        if saved:
            self.messages = saved
            console.print("[dim]已加载上次会话记录[/dim]")
        else:
            self.messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ]

    def _parse_tool_call(self, content: str) -> list:
        """从模型回复中解析工具调用"""
        tools = []
        pattern = r"```tool\s*\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            try:
                tool_data = json.loads(match.strip())
                tools.append(tool_data)
            except json.JSONDecodeError:
                continue
        return tools

    def _extract_text_response(self, content: str) -> str:
        """提取纯文本回复（去掉工具调用部分）"""
        pattern = r"```tool\s*\n.*?\n```"
        text = re.sub(pattern, "", content, flags=re.DOTALL).strip()
        return text

    def chat(self, user_input: str) -> str:
        """处理用户输入，返回回复"""
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL,
                messages=self.messages,
                max_tokens=Config.MAX_OUTPUT_TOKENS,
                temperature=0.7,
            )

            content = response.choices[0].message.content

            # 检查是否有工具调用
            tool_calls = self._parse_tool_call(content)
            text_response = self._extract_text_response(content)

            if text_response:
                self.messages.append({"role": "assistant", "content": text_response})
                console.print()
                console.print(Panel(Markdown(text_response), title="🍚 MiMo", border_style="cyan"))

            # 执行工具调用
            for tool_call in tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})

                console.print(f"\n🔧 执行工具: [yellow]{tool_name}[/yellow]({tool_args})")
                result = self.tools.execute_tool(tool_name, tool_args)

                # 把结果反馈给模型
                tool_msg = f"工具 {tool_name} 执行结果:\n{result}"
                console.print(Panel(result, title=f"📋 {tool_name}", border_style="green"))

                self.messages.append({"role": "user", "content": tool_msg})

                # 继续对话让模型处理工具结果
                follow_up = self.client.chat.completions.create(
                    model=Config.MODEL,
                    messages=self.messages,
                    max_tokens=Config.MAX_OUTPUT_TOKENS,
                    temperature=0.7,
                )
                follow_content = follow_up.choices[0].message.content
                follow_text = self._extract_text_response(follow_content)

                if follow_text:
                    self.messages.append({"role": "assistant", "content": follow_text})
                    console.print()
                    console.print(Panel(Markdown(follow_text), title="🍚 MiMo", border_style="cyan"))

            # 限制历史长度
            if len(self.messages) > Config.MAX_HISTORY * 2:
                system_msg = self.messages[0]
                self.messages = [system_msg] + self.messages[-(Config.MAX_HISTORY * 2):]

            # 保存会话
            self.memory.save_session(self.messages)

            return content

        except Exception as e:
            error_msg = f"[错误] API 调用失败: {e}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

    def reset(self):
        """重置会话"""
        self.memory.archive_session(self.messages)
        self.messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        console.print("[green]✅ 会话已重置[/green]")
