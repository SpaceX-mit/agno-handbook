#!/usr/bin/env python3
"""
测试 MiniMax 连接
"""

import os
import sys

def test_minimax_connection():
    """测试 MiniMax API 连接"""

    print("=" * 70)
    print("MiniMax 连接测试")
    print("=" * 70)

    # 检查 API 密钥
    api_key = os.getenv('MINIMAX_API_KEY')

    if not api_key:
        print("\n❌ 错误: MINIMAX_API_KEY 未设置")
        print("\n请按以下步骤设置:")
        print("1. 访问 https://platform.minimax.io/")
        print("2. 注册并获取 API 密钥")
        print("3. 运行: export MINIMAX_API_KEY='your-key'")
        print("\n或者永久设置:")
        print("echo 'export MINIMAX_API_KEY=\"your-key\"' >> ~/.bashrc")
        print("source ~/.bashrc")
        return False

    print(f"\n✓ API 密钥已设置: {api_key[:10]}...{api_key[-5:]}")

    # 测试导入
    print("\n测试导入模块...")
    try:
        from agno.models.minimax import MiniMax
        from agno.agent import Agent
        print("✓ 模块导入成功")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 创建模型
    print("\n创建 MiniMax 模型...")
    try:
        model = MiniMax(id="MiniMax-M3")
        print(f"✓ 模型创建成功: {model.name} - {model.id}")
        print(f"  API 端点: {model.base_url}")
    except Exception as e:
        print(f"❌ 模型创建失败: {e}")
        return False

    # 创建 agent
    print("\n创建测试 agent...")
    try:
        agent = Agent(
            model=model,
            instructions="你是一个友好的助手，请用简短的中文回答。"
        )
        print("✓ Agent 创建成功")
    except Exception as e:
        print(f"❌ Agent 创建失败: {e}")
        return False

    # 发送测试消息
    print("\n发送测试消息: '你好，请用一句话介绍你自己'")
    print("-" * 70)
    try:
        response = agent.run("你好，请用一句话介绍你自己")
        print(f"\n响应: {response.content}")
        print("-" * 70)
        print("\n✓ 测试成功！MiniMax 连接正常")
        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n可能的原因:")
        print("1. API 密钥无效或已过期")
        print("2. 网络连接问题")
        print("3. 余额不足")
        print("4. 防火墙阻止连接")
        print("\n请检查:")
        print("- 登录 https://platform.minimax.io/ 验证密钥状态")
        print("- 检查账户余额")
        print("- 运行: curl https://api.minimax.io/v1/models")
        return False


if __name__ == "__main__":
    print("\n")
    success = test_minimax_connection()
    print("\n" + "=" * 70)

    if success:
        print("✓ 所有测试通过！")
        print("\n现在可以运行:")
        print("  python cookbook/system_agent/cli_with_llm.py --model minimax")
        sys.exit(0)
    else:
        print("✗ 测试失败，请按照上述提示解决问题")
        sys.exit(1)
