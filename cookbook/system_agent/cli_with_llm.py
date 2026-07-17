#!/usr/bin/env python3
"""
Interactive CLI with MiniMax and Local Llama Support
=====================================================

交互式界面，支持 MiniMax 和本地 Llama 服务器。

使用方法：
    # 使用 MiniMax
    export MINIMAX_API_KEY='your-key'
    python cli_with_llm.py --model minimax

    # 使用本地 Ollama/Llama
    python cli_with_llm.py --model ollama

    # 使用 worker 机器上的 Llama
    python cli_with_llm.py --model worker-llama
"""

import argparse
import os
import sys
from pathlib import Path

from agno.agent import Agent
from agno.tools.file import FileTools
from agno.tools.package_manager import PackageManagerTools
from agno.tools.shell import ShellTools
from agno.tools.system_monitor import SystemMonitorTools


def create_agent(model_type: str) -> Agent:
    """根据模型类型创建agent"""

    instructions = """\
你是一个系统管理员助手，帮助用户通过自然语言管理Linux系统。
始终解释你要做什么，对危险操作进行确认，并提供清晰简洁的响应。
保持响应专业且技术化。使用表格或结构化输出显示多个项目。不使用表情符号。
"""

    # 选择模型
    if model_type == "minimax":
        try:
            from agno.models.minimax import MiniMax
        except ImportError:
            print("错误: MiniMax 模型不可用")
            sys.exit(1)

        if not os.getenv("MINIMAX_API_KEY"):
            print("错误: MINIMAX_API_KEY 未设置")
            print("请运行: export MINIMAX_API_KEY='your-key'")
            sys.exit(1)

        # 支持国内版 minimaxi.com
        base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
        model_id = os.getenv("MINIMAX_MODEL", "MiniMax-M3")  # M3 模型

        model = MiniMax(
            id=model_id,
            base_url=base_url
        )
        print(f"使用模型: MiniMax {model_id}")
        print(f"API端点: {base_url}")

    elif model_type == "ollama":
        try:
            from agno.models.ollama import Ollama
        except ImportError:
            print("错误: ollama 包未安装")
            print("请运行: pip install ollama")
            sys.exit(1)

        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model_id = os.getenv("OLLAMA_MODEL", "llama3.1")
        model = Ollama(id=model_id, host=host)
        print(f"使用模型: Ollama {model_id} @ {host}")

    elif model_type == "worker-llama":
        try:
            from agno.models.ollama import Ollama
        except ImportError:
            print("错误: ollama 包未安装")
            print("请运行: pip install ollama")
            sys.exit(1)

        host = "http://10.0.90.243:11434"
        model_id = os.getenv("OLLAMA_MODEL", "llama3.1")
        model = Ollama(id=model_id, host=host)
        print(f"使用模型: Ollama {model_id} @ {host} (worker机器)")

    else:
        print(f"错误: 未知的模型类型 '{model_type}'")
        print("支持的类型: minimax, ollama, worker-llama")
        sys.exit(1)

    return Agent(
        name="Worker System Assistant",
        model=model,
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
        add_datetime_to_context=True,
    )


def print_welcome(model_type: str):
    """打印欢迎信息"""
    print("\n" + "=" * 70)
    print("  Worker System Agent - AI 系统管理员")
    print("=" * 70)
    print(f"\n当前模型: {model_type.upper()}")
    print("\n使用自然语言输入命令。示例:")
    print("  - 检查系统健康状态")
    print("  - 列出占用内存最多的5个进程")
    print("  - 显示磁盘空间")
    print("  - 查找所有Python文件")
    print("\n命令: 'exit', 'quit', 'bye' 退出 | 'clear' 清屏")
    print("=" * 70 + "\n")


def handle_confirmations(run_response) -> bool:
    """处理确认提示"""
    if not run_response.active_requirements:
        return True

    print("\n" + "-" * 70)
    print("需要确认")
    print("-" * 70)

    for requirement in run_response.active_requirements:
        if requirement.needs_confirmation:
            tool = requirement.tool_execution
            print(f"\n工具: {tool.tool_name}")
            print(f"参数: {tool.tool_args}")
            print()

            while True:
                answer = input("批准此操作? [y/N]: ").strip().lower()
                if answer in ['y', 'yes', 'Y']:
                    requirement.confirm()
                    print("✓ 已批准")
                    break
                elif answer in ['n', 'no', 'N', '']:
                    requirement.reject()
                    print("✗ 已拒绝")
                    return False
                else:
                    print("请回答 'y' 或 'n'")

    print("-" * 70 + "\n")
    return True


def run_repl(model_type: str):
    """运行交互式REPL循环"""
    print_welcome(model_type)

    try:
        agent = create_agent(model_type)
    except Exception as e:
        print(f"创建agent失败: {e}")
        return

    print("Agent 就绪。输入你的命令:\n")

    while True:
        try:
            user_input = input("你: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n再见!")
                break

            if user_input.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                print_welcome(model_type)
                continue

            print("\nAgent: ", end="", flush=True)
            run_response = agent.run(user_input)

            if run_response.active_requirements:
                if handle_confirmations(run_response):
                    run_response = agent.continue_run(
                        run_response,
                        requirements=run_response.requirements
                    )
                    print("\nAgent: ", end="", flush=True)
                    print(run_response.content)
                else:
                    print("\n用户取消了操作。")
            else:
                print(run_response.content)

            print()

        except KeyboardInterrupt:
            print("\n\n中断。输入 'exit' 退出或继续输入命令。\n")
            continue
        except EOFError:
            print("\n\n再见!")
            break
        except Exception as e:
            print(f"\n\n错误: {e}")
            print("请重试。\n")
            continue


def main():
    parser = argparse.ArgumentParser(description="Worker System Agent CLI")
    parser.add_argument(
        "--model",
        choices=["minimax", "ollama", "worker-llama"],
        default="ollama",
        help="选择LLM模型 (默认: ollama)"
    )
    args = parser.parse_args()

    try:
        run_repl(args.model)
    except KeyboardInterrupt:
        print("\n\n再见!")
        sys.exit(0)


if __name__ == "__main__":
    main()
