#!/usr/bin/env python3
"""测试 MiniMax CN 连接"""

import os
import sys

# 设置你的配置
os.environ["MINIMAX_API_KEY"] = "sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
os.environ["MINIMAX_BASE_URL"] = "https://api.minimaxi.com/v1"

sys.path.insert(0, 'libs/agno')

print("=" * 70)
print("MiniMax CN 连接测试")
print("=" * 70)

try:
    from agno.models.minimax import MiniMax
    from agno.agent import Agent

    print("\n创建模型...")
    model = MiniMax(
        id="abab6.5s-chat",
        base_url="https://api.minimaxi.com/v1"
    )
    print(f"✓ 模型: {model.id}")
    print(f"✓ 端点: {model.base_url}")

    print("\n创建测试agent...")
    agent = Agent(
        model=model,
        instructions="你是一个友好的助手，请用简短的中文回答。"
    )

    print("\n发送测试消息: '你好，请用一句话介绍你自己'")
    print("-" * 70)
    response = agent.run("你好，请用一句话介绍你自己")
    print(f"\n响应: {response.content}")
    print("-" * 70)

    print("\n✓ MiniMax CN 连接成功！")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    print("\n请检查:")
    print("1. API密钥是否正确")
    print("2. 网络连接到 api.minimaxi.com")
    print("3. 模型名称是否正确")
    import traceback
    traceback.print_exc()
    sys.exit(1)

