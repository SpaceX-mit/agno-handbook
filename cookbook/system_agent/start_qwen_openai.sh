#!/bin/bash
# Worker System Agent with Qwen3.5-2B via OpenAI-compatible API

set -e

echo "========================================================================"
echo "  Worker System Agent - Qwen3.5-2B (OpenAI API 模式)"
echo "========================================================================"
echo

LLAMA_SERVER_HOST="http://localhost:11434"

# 检查 llama-server
echo "检查 llama-server 状态..."
if ! curl -s "$LLAMA_SERVER_HOST/health" > /dev/null 2>&1; then
    echo "❌ llama-server 未运行"
    echo "启动命令: ./cookbook/system_agent/start_qwen_server.sh"
    exit 1
fi

echo "✓ llama-server 运行正常"
echo

# 激活虚拟环境
source .venv/bin/activate
echo "✓ 虚拟环境已激活"
echo

# 使用 OpenAI 兼容 API
python3 << 'PYEOF'
import sys
sys.path.insert(0, 'libs/agno')

from agno.models.openai import OpenAIChat
from agno.agent import Agent
from agno.tools.system_monitor import SystemMonitorTools
from agno.tools.file import FileTools
from pathlib import Path

print("创建 Qwen3.5-2B agent (OpenAI API 兼容模式)...\n")

# 使用 OpenAI 兼容的 llama-server
model = OpenAIChat(
    id="gpt-3.5-turbo",  # llama-server 接受任意模型名
    api_key="not-needed",  # llama-server 不需要真实密钥
    base_url="http://localhost:11434/v1"  # OpenAI 兼容端点
)

agent = Agent(
    name="Qwen系统助手",
    model=model,
    tools=[
        SystemMonitorTools(),
        FileTools(base_dir=Path("/home/bianbu/agno-riscv64"), all=True)
    ],
    instructions="你是Linux系统管理员助手。简洁回答，用中文。"
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
        if query.lower() in ['exit', 'quit', 'bye']:
            print("\n再见！")
            break

        print("\nAgent: ", end="", flush=True)
        response = agent.run(query)
        print(response.content)
        print()

    except KeyboardInterrupt:
        print("\n\n再见！")
        break
    except Exception as e:
        print(f"\n错误: {e}\n")
        continue
PYEOF
