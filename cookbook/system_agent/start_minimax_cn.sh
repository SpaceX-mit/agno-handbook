#!/bin/bash
# MiniMax CN (minimaxi.com) 配置和启动脚本

set -e

echo "========================================================================"
echo "  MiniMax CN (minimaxi.com) 配置"
echo "========================================================================"
echo

# 设置你的配置 - 必须在这里设置
export MINIMAX_API_KEY="sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
export MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
export MINIMAX_MODEL="MiniMax-M3"

echo "✓ MiniMax 配置:"
echo "  API端点: $MINIMAX_BASE_URL"
echo "  模型: $MINIMAX_MODEL"
echo "  API密钥: ${MINIMAX_API_KEY:0:15}...${MINIMAX_API_KEY: -10}"
echo

# 检查环境变量是否设置
if [ -z "$MINIMAX_MODEL" ]; then
    echo "❌ 错误: MINIMAX_MODEL 未设置"
    exit 1
fi

echo "验证环境变量:"
echo "  MINIMAX_MODEL=$MINIMAX_MODEL"
echo

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    echo "请运行: ./scripts/dev_setup.sh"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate
echo "✓ 虚拟环境已激活"
echo

# 测试连接
echo "========================================================================"
echo "测试 MiniMax CN 连接"
echo "========================================================================"
echo

python3 << 'PYTHON_TEST'
import os
import sys

try:
    from agno.models.minimax import MiniMax
    from agno.agent import Agent

    print("创建模型...")
    model = MiniMax(
        id=os.getenv("MINIMAX_MODEL", "abab6.5s-chat"),
        base_url=os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
    )
    print(f"✓ 模型: {model.id}")
    print(f"✓ 端点: {model.base_url}")

    print("\n创建测试agent...")
    agent = Agent(
        model=model,
        instructions="你是一个友好的助手，请用简短的中文回答。"
    )

    print("\n发送测试消息...")
    response = agent.run("你好，请用一句话介绍你自己")
    print(f"\n响应: {response.content}\n")

    print("=" * 70)
    print("✓ MiniMax CN 连接成功！")
    print("=" * 70)
    sys.exit(0)

except Exception as e:
    print(f"\n❌ 连接失败: {e}\n")
    print("请检查:")
    print("1. API密钥是否正确")
    print("2. 网络连接是否正常")
    print("3. API端点是否可访问")
    print(f"\n测试命令: curl {os.getenv('MINIMAX_BASE_URL', 'https://api.minimaxi.com/v1')}")
    sys.exit(1)
PYTHON_TEST

if [ $? -eq 0 ]; then
    echo
    echo "========================================================================"
    echo "启动 Worker System Agent"
    echo "========================================================================"
    echo
    python cookbook/system_agent/cli_with_llm.py --model minimax
else
    echo
    echo "连接测试失败，请检查配置后重试"
    exit 1
fi
