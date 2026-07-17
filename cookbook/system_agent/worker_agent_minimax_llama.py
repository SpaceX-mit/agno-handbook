"""
Worker System Agent with MiniMax and Local Llama
=================================================

配置使用 MiniMax 云服务和本地 Llama 服务器作为 LLM 提供商。

支持的模型：
1. MiniMax (云服务) - 需要 MINIMAX_API_KEY
2. Ollama (本地) - 连接到本地 llama-server

环境变量：
- MINIMAX_API_KEY: MiniMax API密钥
- OLLAMA_HOST: Ollama服务地址 (默认: http://localhost:11434)
"""

from pathlib import Path

from agno.agent import Agent
from agno.models.minimax import MiniMax
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from agno.tools.package_manager import PackageManagerTools
from agno.tools.shell import ShellTools
from agno.tools.system_monitor import SystemMonitorTools

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
你是一个 RISC-V Linux 系统的系统管理员助手。

## 你的角色

通过自然语言帮助用户管理和监控Linux系统。你可以：
- 监控系统资源（CPU、内存、磁盘、网络、进程）
- 安全地执行shell命令
- 管理文件和目录
- 搜索和安装/删除软件包
- 检查服务状态
- 提供系统诊断和建议

## 安全协议

1. **危险操作前必须确认**：
   - 删除文件或目录
   - 终止进程
   - 安装或删除软件包
   - 运行会修改系统状态的命令

2. **执行前说明**：
   - 描述命令的作用
   - 显示将要运行的实际命令
   - 警告潜在风险

3. **建议更安全的替代方案**：
   - 请求高风险操作时，提出更安全的选项
   - 在执行密集操作前检查系统资源
   - 验证路径和输入

4. **错误处理**：
   - 清楚地解释错误
   - 建议排查步骤
   - 在有帮助时提供相关文档链接

## 响应风格

- **简洁专业**：假设用户了解Linux
- **结构化输出**：使用表格、列表或代码块以提高清晰度
- **清晰的指标**：格式化数字以便阅读（GB、%等）
- **面向行动**：提供下一步或建议
- **不使用表情符号**：保持专业

## 工作流程

1. **理解请求**：澄清模糊的查询
2. **检查前提条件**：如需要则验证系统状态
3. **安全执行**：使用适当的工具和确认
4. **清晰报告**：以可读格式显示结果
5. **建议下一步**：推荐后续操作
"""

# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------

# 选项1: MiniMax (云服务)
# 需要设置环境变量: export MINIMAX_API_KEY='your-key'
# 如果使用 minimaxi.com (国内版)，需要设置 base_url
minimax_model = MiniMax(
    id="abab6.5s-chat",  # 或 "abab6.5-chat", "abab5.5-chat" 等
    base_url="https://api.minimaxi.com/v1",  # 国内版端点
)

# 选项2: 本地 Ollama/Llama
# 确保 llama-server 运行在 localhost:11434
ollama_model = Ollama(
    id="llama3.1",  # 或其他本地模型如 "llama3.2", "qwen2.5"
    host="http://localhost:11434",  # llama-server 地址
)

# 选项3: 使用worker机器上的llama-server
# 如果llama-server运行在worker机器上
worker_llama_model = Ollama(
    id="llama3.1",
    host="http://10.0.90.243:11434",  # worker机器地址
)

# ---------------------------------------------------------------------------
# 选择要使用的模型
# ---------------------------------------------------------------------------
# 方式1: 使用 MiniMax (推荐，功能最强)
selected_model = minimax_model

# 方式2: 使用本地 Llama
# selected_model = ollama_model

# 方式3: 使用 worker 机器上的 Llama
# selected_model = worker_llama_model

# ---------------------------------------------------------------------------
# Create the Worker System Agent
# ---------------------------------------------------------------------------
worker_system_agent = Agent(
    name="Worker System Assistant",
    model=selected_model,
    instructions=instructions,
    tools=[
        SystemMonitorTools(),
        ShellTools(
            base_dir="/home/bianbu/agno-riscv64",
            requires_confirmation_tools=["run_shell_command"]
        ),
        FileTools(
            base_dir=Path("/home/bianbu/agno-riscv64"),
            enable_delete_file=True,
            all=True,
        ),
        PackageManagerTools(
            requires_confirmation_tools=[
                "install_package",
                "remove_package",
                "upgrade_packages",
            ]
        ),
    ],
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_context=True,
)

# ---------------------------------------------------------------------------
# Run the Agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    # 检查配置
    print("=" * 70)
    print("Worker System Agent - LLM 配置")
    print("=" * 70)
    print(f"模型: {selected_model.name} - {selected_model.id}")
    print(f"提供商: {selected_model.provider}")

    if isinstance(selected_model, MiniMax):
        print(f"API端点: {selected_model.base_url}")
        if not selected_model.api_key:
            print("\n⚠️  警告: MINIMAX_API_KEY 未设置")
            print("请运行: export MINIMAX_API_KEY='your-key'\n")
            sys.exit(1)
    elif isinstance(selected_model, Ollama):
        host = selected_model.host or "http://localhost:11434"
        print(f"Ollama主机: {host}")
        print("\n确保 llama-server 正在运行:")
        print(f"  curl {host}/api/tags\n")

    print("=" * 70)
    print()

    # 运行示例查询
    worker_system_agent.print_response(
        "检查系统健康状态 - 显示CPU使用率、内存和磁盘空间",
        stream=True
    )
