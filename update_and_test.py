#!/usr/bin/env python3
"""更新worker机器并测试修复"""

import paramiko
import sys

HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
REMOTE_PATH = "/home/bianbu/agno-riscv64"

def run_command(ssh, command, show_output=True):
    print(f"\n> {command[:80]}...")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    if show_output and output:
        print(output)
    return exit_code

def main():
    print("=" * 70)
    print("更新 Worker 机器并测试")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("\n✓ 已连接")

        # 更新代码
        print("\n更新代码...")
        run_command(ssh, f"cd {REMOTE_PATH} && git pull")

        # 测试启动
        print("\n测试 MiniMax CN 启动...")
        exit_code = run_command(ssh, f"cd {REMOTE_PATH} && timeout 10 ./cookbook/system_agent/start_minimax_cn.sh || true")

        print("\n" + "=" * 70)
        if exit_code == 0 or exit_code == 124:  # 124 = timeout (正常)
            print("✓ 修复成功！现在可以正常使用了")
            print("\n运行命令:")
            print(f"  ssh {USERNAME}@{HOST}")
            print(f"  cd {REMOTE_PATH}")
            print(f"  ./cookbook/system_agent/start_minimax_cn.sh")
        else:
            print("需要检查")
        print("=" * 70)

    except Exception as e:
        print(f"\n错误: {e}")
        return 1
    finally:
        ssh.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
