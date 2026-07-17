#!/usr/bin/env python3
"""在worker机器上快速测试MiniMax agent"""

import paramiko
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("10.0.90.243", username="bianbu", password="bianbu", timeout=10)
    print("✓ 已连接到worker机器\n")

    # 测试agent创建和简单查询
    test_script = """
cd /home/bianbu/agno-riscv64
source .venv/bin/activate

export MINIMAX_API_KEY="sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
export MINIMAX_BASE_URL="https://api.minimaxi.com/v1"

python3 << 'PYEOF'
import sys
sys.path.insert(0, 'libs/agno')

from agno.models.minimax import MiniMax
from agno.agent import Agent
from agno.tools.system_monitor import SystemMonitorTools

print("创建 MiniMax agent...")
model = MiniMax(id="abab6.5s-chat", base_url="https://api.minimaxi.com/v1")

agent = Agent(
    name="测试Agent",
    model=model,
    tools=[SystemMonitorTools()],
    instructions="你是系统助手，回答要简洁。"
)

print("✓ Agent 创建成功\\n")
print("发送测试查询: 获取系统信息")
print("-" * 50)

response = agent.run("获取系统信息，只显示OS和架构")
print(response.content)

print("-" * 50)
print("\\n✓ 测试完成！Agent 工作正常")
PYEOF
"""

    print("运行测试...")
    print("=" * 70)
    stdin, stdout, stderr = ssh.exec_command(test_script, timeout=60)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode()
    error = stderr.read().decode()

    print(output)
    if error and exit_code != 0:
        print("STDERR:", error)

    print("=" * 70)

    if exit_code == 0:
        print("\n✓ 所有测试通过！")
        print("\n现在你可以:")
        print("  ssh bianbu@10.0.90.243")
        print("  cd /home/bianbu/agno-riscv64")
        print("  ./cookbook/system_agent/start_minimax_cn.sh")
        print("\n然后用中文自然语言管理系统！")
    else:
        print(f"\n✗ 测试失败 (退出码: {exit_code})")

except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
finally:
    ssh.close()
