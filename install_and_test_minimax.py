#!/usr/bin/env python3
"""在worker机器上安装依赖并测试MiniMax CN"""

import paramiko
import sys

HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
REMOTE_PATH = "/home/bianbu/agno-riscv64"

MINIMAX_API_KEY = "sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"


def run_command(ssh, command, show_output=True, timeout=300):
    print(f"\n> {command[:100]}{'...' if len(command) > 100 else ''}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if show_output and output:
        print(output)
    if error and exit_code != 0:
        print(f"STDERR: {error}")
    return exit_code, output, error


def main():
    print("=" * 70)
    print("在 Worker 机器上安装依赖并测试 MiniMax CN")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✓ 已连接\n")

        # 安装依赖
        print("安装 openai 依赖...")
        run_command(ssh, f"cd {REMOTE_PATH} && .venv/bin/pip install openai", timeout=600)

        # 测试MiniMax CN
        print("\n测试 MiniMax CN 连接...")
        print("-" * 70)

        test_cmd = f"""
cd {REMOTE_PATH}
source .venv/bin/activate
export MINIMAX_API_KEY="{MINIMAX_API_KEY}"
export MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
python3 -c '
from agno.models.minimax import MiniMax
from agno.agent import Agent
import os

model = MiniMax(id="abab6.5s-chat", base_url=os.getenv("MINIMAX_BASE_URL"))
print("✓ 模型创建成功:", model.id)

agent = Agent(model=model, instructions="你是助手")
print("\\n测试消息: 你好")
response = agent.run("你好，用一句话介绍你自己")
print("响应:", response.content)
print("\\n✓ MiniMax CN 工作正常！")
'
"""
        exit_code, output, error = run_command(ssh, test_cmd, timeout=120)

        if exit_code == 0:
            print("\n" + "=" * 70)
            print("✓ 部署成功！MiniMax CN 已在 worker 机器上运行")
            print("=" * 70)
            print("\n使用方法:")
            print(f"  ssh {USERNAME}@{HOST}")
            print(f"  cd {REMOTE_PATH}")
            print(f"  ./cookbook/system_agent/start_minimax_cn.sh")
            return 0
        else:
            print("\n✗ 测试失败")
            return 1

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        return 1
    finally:
        ssh.close()


if __name__ == "__main__":
    sys.exit(main())
