#!/usr/bin/env python3
"""
Worker System Agent with Qwen3.5-2B via OpenAI-compatible API

使用本地 Qwen3.5-2B 模型（通过 llama-server 的 OpenAI 兼容 API）
运行系统管理助手。

用法:
    python qwen_agent.py
"""

import sys
from pathlib import Path

# 添加 agno 库路径
sys.path.insert(0, "libs/agno")

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools
from agno.tools.system_monitor import SystemMonitorTools


def main():
    print("创建 Qwen3.5-2B agent (OpenAI API 兼容模式)...\n")

    # 使用 OpenAI 兼容的 llama-server
    model = OpenAIChat(
        id="gpt-3.5-turbo",  # llama-server 接受任意模型名
        api_key="not-needed",  # llama-server 不需要真实密钥
        base_url="http://localhost:11434/v1",  # OpenAI 兼容端点
    )

    agent = Agent(
        name="Qwen系统助手",
        model=model,
        tools=[
            SystemMonitorTools(),
            FileTools(
                base_dir=Path("/home/bianbu/agno-riscv64"),
                enable_read_file=True,
                enable_list_files=True,
                enable_search_files=True,
                # 关闭较少用的功能以减少工具定义 token 占用
                enable_save_file=False,
                enable_search_content=False,
                enable_read_file_chunk=False,
                enable_replace_file_chunk=False,
            ),
        ],
        instructions="你是Linux系统管理员助手。简洁回答，用中文。",
    )

    print("✓ Agent 就绪\n")
    print("=" * 70)
    print("Qwen3.5-2B 本地模型 - 交互模式")
    print("=" * 70)
    print("输入 'exit' 退出\n")

    while True:
        try:
            query = input("你: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "bye"]:
                print("\n再见！")
                break

            print("\nAgent: ", end="", flush=True)
            response = agent.run(query)
            print(response.content)
            print()

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except EOFError:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}\n")
            continue


if __name__ == "__main__":
    main()
