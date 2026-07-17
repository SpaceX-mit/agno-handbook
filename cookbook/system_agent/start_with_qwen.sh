#!/bin/bash
# Worker System Agent with Qwen3.5-2B Local Model

set -e

echo "========================================================================"
echo "  Worker System Agent - Qwen3.5-2B 本地模型"
echo "========================================================================"
echo

# 配置
LLAMA_SERVER_HOST="http://localhost:11434"
MODEL_PATH="/home/bianbu/models/Qwen3.5-2B-Q4_0.gguf"

# 检查 llama-server 是否运行
echo "检查 llama-server 状态..."
if ! curl -s "$LLAMA_SERVER_HOST/health" > /dev/null 2>&1; then
    echo "❌ 错误: llama-server 未运行"
    echo
    echo "请先启动 llama-server:"
    echo "  ./cookbook/system_agent/start_qwen_server.sh"
    echo
    echo "或者在后台启动:"
    echo "  nohup ./cookbook/system_agent/start_qwen_server.sh > qwen_server.log 2>&1 &"
    exit 1
fi

echo "✓ llama-server 运行正常"
echo "  地址: $LLAMA_SERVER_HOST"
echo

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate
echo "✓ 虚拟环境已激活"
echo

# 使用 llama-cpp-python 直接加载模型（不通过HTTP）
echo "========================================================================"
echo "启动 Worker System Agent (Qwen3.5-2B)"
echo "========================================================================"
echo

python3 << 'PYEOF'
import sys
sys.path.insert(0, 'libs/agno')

from agno.models.ollama import Ollama
from agno.agent import Agent
from agno.tools.system_monitor import SystemMonitorTools
from agno.tools.file import FileTools
from pathlib import Path

print("创建 Qwen3.5-2B agent (通过 llama-server)...")

# 使用 Ollama 模型连接到 llama-server
model = Ollama(
    id="qwen",  # 使用简单的ID
    host="http://localhost:11434"
)

agent = Agent(
    name="Worker系统助手",
    model=model,
    tools=[
        SystemMonitorTools(),
        FileTools(base_dir=Path("/home/bianbu/agno-riscv64"), all=True)
    ],
    instructions="你是专业的Linux系统管理员助手。回答简洁准确，使用中文。"
)

print("✓ Agent 创建成功")
print("\n开始交互式会话...")
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

