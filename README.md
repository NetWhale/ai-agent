# 🍚 MiMo Agent

基于 MiMo API 的 CLI 交互式 AI 助手。

## 功能

- **CLI 交互式对话** - 多轮上下文，自然对话
- **工具调用** - 读写文件、执行命令、搜索内容
- **项目感知** - 自动检测项目类型和结构
- **安全防护** - 危险命令拦截、敏感文件保护
- **记忆系统** - 跨会话保持对话和笔记

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API
cp .env.example .env
# 编辑 .env，填入你的 MiMo API Key

# 3. 启动
python main.py

# 指定工作目录
python main.py -d /path/to/project
```

## 内置命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/reset` | 重置会话 |
| `/context` | 显示项目上下文 |
| `/notes` | 显示笔记 |
| `/clear` | 清屏 |
| `/quit` | 退出 |

## 项目结构

```
ai-agent/
├── main.py          # CLI 入口
├── agent.py         # 核心 agent 逻辑
├── tools.py         # 工具系统
├── context.py       # 项目上下文
├── memory.py        # 记忆系统
├── safety.py        # 安全检查
├── config.py        # 配置管理
├── requirements.txt
└── .env.example
```

## 工具调用

AI 可以在回复中使用工具：

```tool
{
  "name": "read_file",
  "args": {"path": "src/main.py"}
}
```

可用工具：
- `read_file(path)` - 读取文件
- `write_file(path, content)` - 写入文件
- `exec_command(command)` - 执行命令
- `list_files(path)` - 列出目录
- `search_files(pattern, path)` - 搜索内容

## 安全机制

- 危险命令拦截（rm -rf、fork bomb 等）
- 敏感文件保护（.env、密钥文件等）
- 命令执行确认（sudo、rm 等需确认）
- 命令执行超时限制（30s）
- 文件大小限制（读取 1MB 以内）
