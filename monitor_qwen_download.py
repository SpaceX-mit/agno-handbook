#!/usr/bin/env python3
"""监控 Qwen3.5-2B 模型下载进度并自动部署"""

import paramiko
import time
import sys

HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
MODEL_PATH = "/home/bianbu/models/Qwen3.5-2B-Q4_0.gguf"

def check_download_status(ssh):
    """检查下载状态"""
    # 检查文件是否存在
    stdin, stdout, stderr = ssh.exec_command(f"test -f {MODEL_PATH} && echo 'exists' || echo 'not_exists'")
    stdout.channel.recv_exit_status()
    status = stdout.read().decode().strip()

    if status == 'exists':
        # 获取文件大小
        stdin, stdout, stderr = ssh.exec_command(f"ls -lh {MODEL_PATH}")
        stdout.channel.recv_exit_status()
        file_info = stdout.read().decode().strip()
        return True, file_info
    else:
        # 检查临时文件（下载中）
        stdin, stdout, stderr = ssh.exec_command(f"ls -lh {MODEL_PATH}.tmp 2>/dev/null || echo 'not found'")
        stdout.channel.recv_exit_status()
        temp_info = stdout.read().decode().strip()

        # 检查下载进程
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep wget | grep Qwen3.5 | grep -v grep")
        stdout.channel.recv_exit_status()
        process_info = stdout.read().decode().strip()

        return False, f"临时文件: {temp_info}\n进程: {'运行中' if process_info else '未运行'}"

def deploy_scripts(ssh):
    """部署脚本到worker机器"""
    print("\n部署脚本到worker机器...")

    # 1. 更新代码
    stdin, stdout, stderr = ssh.exec_command("cd /home/bianbu/agno-riscv64 && git pull")
    stdout.channel.recv_exit_status()
    print(stdout.read().decode())

    # 2. 设置执行权限
    stdin, stdout, stderr = ssh.exec_command("chmod +x /home/bianbu/agno-riscv64/cookbook/system_agent/*.sh")
    stdout.channel.recv_exit_status()
    print("✓ 脚本权限已设置")

    return True

def test_qwen_model(ssh):
    """测试Qwen模型"""
    print("\n测试 Qwen3.5-2B 模型...")

    test_script = f"""
cd /home/bianbu/agno-riscv64
source .venv/bin/activate

# 检查 llama-server
if ! which llama-server > /dev/null 2>&1; then
    echo "❌ llama-server 未安装"
    exit 1
fi

echo "✓ llama-server 已安装: $(which llama-server)"

# 测试启动 llama-server（dry-run）
llama-server --version 2>&1 | head -3 || echo "无版本信息"

echo ""
echo "准备就绪！可以启动服务："
echo "  ./cookbook/system_agent/start_qwen_server.sh"
"""

    stdin, stdout, stderr = ssh.exec_command(test_script, timeout=30)
    stdout.channel.recv_exit_status()
    print(stdout.read().decode())

def main():
    print("=" * 70)
    print("Qwen3.5-2B 模型下载监控")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=10)
        print("✓ 已连接到worker机器\n")

        # 检查下载状态
        completed, info = check_download_status(ssh)

        if completed:
            print("✓ 模型已下载完成！")
            print(f"  {info}\n")

            # 部署脚本
            if deploy_scripts(ssh):
                print("✓ 脚本部署完成\n")

                # 测试环境
                test_qwen_model(ssh)

                print("\n" + "=" * 70)
                print("✓ 所有准备工作完成！")
                print("=" * 70)
                print("\n使用方法:")
                print("  ssh bianbu@10.0.90.243")
                print("  cd /home/bianbu/agno-riscv64")
                print("\n  # 启动 llama-server")
                print("  ./cookbook/system_agent/start_qwen_server.sh")
                print("\n  # 启动 System Agent")
                print("  ./cookbook/system_agent/start_with_qwen.sh")

        else:
            print("⏳ 模型仍在下载中...")
            print(f"{info}\n")
            print("继续监控...")
            print("  python3 monitor_qwen_download.py")

            # 显示下载日志最后几行
            print("\n最新日志:")
            stdin, stdout, stderr = ssh.exec_command("tail -5 /home/bianbu/models/download.log")
            stdout.channel.recv_exit_status()
            print(stdout.read().decode())

    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        ssh.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
