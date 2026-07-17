#!/bin/bash
# Worker System Agent with Qwen3.5-2B (修复版)

set -e

echo "========================================================================"
echo "  Worker System Agent - Qwen3.5-2B 本地模型"
echo "========================================================================"
echo

LLAMA_SERVER_HOST="http://localhost:11434"
MODEL_PATH="/home/bianbu/models/Qwen3.5-2B-Q4_0.gguf"

# 检查 llama-server，如未运行则自动启动
if ! curl -s "$LLAMA_SERVER_HOST/health" > /dev/null 2>&1; then
    echo "llama-server 未运行，正在启动..."
    pkill -9 llama-server 2>/dev/null || true
    sleep 2
    nohup llama-server \
        --model "$MODEL_PATH" \
        --host 0.0.0.0 \
        --port 11434 \
        --ctx-size 4096 \
        --threads 8 \
        > llama_server.log 2>&1 &

    echo "等待服务就绪..."
    for i in $(seq 1 15); do
        if curl -s "$LLAMA_SERVER_HOST/health" > /dev/null 2>&1; then
            break
        fi
        sleep 2
    done
fi

if ! curl -s "$LLAMA_SERVER_HOST/health" > /dev/null 2>&1; then
    echo "❌ llama-server 启动失败，请检查 llama_server.log"
    exit 1
fi

echo "✓ llama-server 运行正常"
echo

# 激活虚拟环境
source .venv/bin/activate
echo "✓ 虚拟环境已激活"
echo

# 运行 Python 脚本（关键：用文件方式运行，保持 stdin 为终端）
python3 cookbook/system_agent/qwen_agent.py
