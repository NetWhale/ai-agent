"""安全检查模块"""

import re


# 危险命令黑名单
DANGEROUS_PATTERNS = [
    r"rm\s+(-rf?|--recursive)\s+[/~]",
    r"rm\s+(-rf?|--recursive)\s+\*",
    r"mkfs\.",
    r"dd\s+if=",
    r"wipefs",
    r"shred",
    r">\s*/dev/sd",
    r"chmod\s+777\s+/",
    r":\(\)\s*\{.*\|.*&\s*\};",  # fork bomb
    r"curl.*\|\s*(ba)?sh",
    r"wget.*\|\s*(ba)?sh",
    r"nc\s+-[el]",  # netcat listener
    r"bash\s+-i\s+>&",
    r"python.*-c.*socket",
]

# 敏感文件路径
SENSITIVE_PATHS = [
    "/etc/passwd",
    "/etc/shadow",
    "~/.ssh/",
    "~/.gnupg/",
    ".env",
    "*.key",
    "*.pem",
]


class SafetyCheck:
    @staticmethod
    def check_command(command: str) -> tuple[bool, str]:
        """检查命令是否安全"""
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"危险操作被拦截: 匹配规则 {pattern}"
        return True, ""

    @staticmethod
    def check_file_access(path: str) -> tuple[bool, str]:
        """检查文件访问是否涉及敏感路径"""
        for sensitive in SENSITIVE_PATHS:
            if sensitive in path or path.endswith((".key", ".pem")):
                return False, f"敏感文件访问被拦截: {path}"
        return True, ""

    @staticmethod
    def confirm_dangerous(command: str) -> bool:
        """对可能危险的操作进行确认"""
        warning_keywords = ["sudo", "rm", "mv", "kill", "pkill", "systemctl"]
        for kw in warning_keywords:
            if kw in command.lower():
                return True
        return False
