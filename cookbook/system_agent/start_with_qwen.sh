#!/bin/bash
# Worker System Agent with Qwen3.5-2B Local Model

set -e

echo "========================================================================"
echo "  Worker System Agent - Qwen3.5-2B 本地模型"
echo "========================================================================"
echo

# 配置
LLAMA_SERVER_HOST="http://localhost:11434"
MODEL_NAME="Qwen3.5-2B-Q4_0"

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

# 测试连接
echo "========================================================================"
echo "测试 Qwen3.5-2B 连接"
echo "========================================================================"
echo

python3 << 'PYEOF'
import sys
sys.path.insert(0, 'libs/agno')

from agno.models.ollama import Ollama
from agno.agent import Agent

print("创建 Qwen3.5-2B 模型...")
model = Ollama(
    id="Qwen3.5-2B-Q4_0",
    host="http://localhost:11434"
)
print(f"✓ 模型: {model.id}")

print("\n创建测试agent...")
agent = Agent(
    model=model,
    instructions="你是一个友好的助手，用中文简洁回答。"
)

print("\n发送测试消息...")
response = agent.run("你好，请用一句话介绍你自己")
print(f"\n响应: {response.content}")

print("\n✓ Qwen3.5-2B 连接成功！")
PYEOF

if [ $? -eq 0 ]; then
    echo
    echo "========================================================================"
    echo "启动 Worker System Agent"
    echo "========================================================================"
    echo

    # 设置环境变量
    export OLLAMA_HOST="http://localhost:11434"
    export OLLAMA_MODEL="Qwen3.5-2B-Q4_0"

    # 启动 agent
    python cookbook/system_agent/cli_with_llm.py --model ollama
else
    echo
    echo "❌ 连接测试失败"
    exit 1
fi
