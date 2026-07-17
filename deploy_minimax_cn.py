#!/usr/bin/env python3
"""在worker机器上部署并测试MiniMax CN配置"""

import paramiko
import sys

HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
REMOTE_PATH = "/home/bianbu/agno-riscv64"

# MiniMax CN 配置
MINIMAX_API_KEY = "sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
MINIMAX_MODEL = "abab6.5s-chat"


def run_command(ssh, command, show_output=True, timeout=120):
    """Execute command on remote machine."""
    print(f"\n> {command}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if show_output:
        if output:
            print(output)
        if error and exit_code != 0:
            print(f"STDERR: {error}")

    return exit_code, output, error


def main():
    print("=" * 70)
    print("在 Worker 机器上部署并测试 MiniMax CN")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接到 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✓ 已连接\n")

        # Step 1: 更新代码
        print("步骤 1: 拉取最新代码")
        print("-" * 70)
        run_command(ssh, f"cd {REMOTE_PATH} && git pull")

        # Step 2: 设置环境变量并测试
        print("\n步骤 2: 测试 MiniMax CN 连接")
        print("-" * 70)

        test_script = f"""
export MINIMAX_API_KEY="{MINIMAX_API_KEY}"
export MINIMAX_BASE_URL="{MINIMAX_BASE_URL}"
export MINIMAX_MODEL="{MINIMAX_MODEL}"

cd {REMOTE_PATH}
source .venv/bin/activate

python3 << 'PYEOF'
import os
import sys
sys.path.insert(0, 'libs/agno')

print("配置信息:")
print(f"  API端点: {{os.getenv('MINIMAX_BASE_URL')}}")
print(f"  模型: {{os.getenv('MINIMAX_MODEL')}}")
print(f"  API密钥: {{os.getenv('MINIMAX_API_KEY')[:15]}}...{{os.getenv('MINIMAX_API_KEY')[-10:]}}")

try:
    from agno.models.minimax import MiniMax
    from agno.agent import Agent

    print("\\n创建模型...")
    model = MiniMax(
        id=os.getenv('MINIMAX_MODEL'),
        base_url=os.getenv('MINIMAX_BASE_URL')
    )
    print(f"✓ 模型创建成功: {{model.id}}")

    print("\\n创建agent...")
    agent = Agent(
        model=model,
        instructions="你是一个系统管理员助手。"
    )

    print("\\n发送测试消息: '你好，请用一句话介绍你自己'")
    response = agent.run("你好，请用一句话介绍你自己")
    print(f"\\n响应: {{response.content}}")

    print("\\n✓ MiniMax CN 测试成功！")

except Exception as e:
    print(f"\\n✗ 测试失败: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
"""

        exit_code, output, error = run_command(ssh, test_script, timeout=60)

        if exit_code == 0:
            print("\n" + "=" * 70)
            print("✓ 部署和测试成功！")
            print("=" * 70)
            print("\n现在可以在 worker 机器上使用 MiniMax CN:")
            print(f"\n  ssh {USERNAME}@{HOST}")
            print(f"  cd {REMOTE_PATH}")
            print(f"  ./cookbook/system_agent/start_minimax_cn.sh")
            print("\n或者手动运行:")
            print(f'  export MINIMAX_API_KEY="{MINIMAX_API_KEY}"')
            print(f'  export MINIMAX_BASE_URL="{MINIMAX_BASE_URL}"')
            print(f"  python cookbook/system_agent/cli_with_llm.py --model minimax")
            return 0
        else:
            print("\n" + "=" * 70)
            print("✗ 测试失败")
            print("=" * 70)
            return 1

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()


if __name__ == "__main__":
    sys.exit(main())
