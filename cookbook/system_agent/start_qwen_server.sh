#!/bin/bash
# 启动 Qwen3.5-2B 本地模型服务

set -e

MODEL_PATH="/home/bianbu/models/Qwen3.5-2B-Q4_0.gguf"
HOST="0.0.0.0"
PORT="11434"

echo "========================================================================"
echo "  Qwen3.5-2B Llama Server 启动脚本"
echo "========================================================================"
echo

# 检查模型文件
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ 错误: 模型文件不存在"
    echo "路径: $MODEL_PATH"
    echo
    echo "请先下载模型:"
    echo "  cd /home/bianbu/models"
    echo "  wget https://archive.spacemit.com/spacemit-ai/model_zoo/llm/Qwen3.5-2B-Q4_0.gguf"
    exit 1
fi

echo "✓ 模型文件存在"
echo "  路径: $MODEL_PATH"
echo "  大小: $(ls -lh $MODEL_PATH | awk '{print $5}')"
echo

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠ 警告: 端口 $PORT 已被占用"
    echo "现有进程:"
    lsof -Pi :$PORT -sTCP:LISTEN
    echo
    read -p "是否停止现有进程并重启? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "停止现有进程..."
        lsof -Pi :$PORT -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        echo "已取消"
        exit 0
    fi
fi

# 启动 llama-server
echo "启动 llama-server..."
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  模型: Qwen3.5-2B-Q4_0"
echo
echo "========================================================================"
echo

llama-server \
    --model "$MODEL_PATH" \
    --host "$HOST" \
    --port "$PORT" \
    --ctx-size 4096 \
    --n-gpu-layers 99 \
    --threads 8 \
    --log-disable

# 如果上面的命令失败，提供帮助信息
if [ $? -ne 0 ]; then
    echo
    echo "❌ llama-server 启动失败"
    echo
    echo "可能的原因:"
    echo "1. llama-server 未安装"
    echo "2. 模型文件损坏"
    echo "3. 内存不足"
    echo
    echo "检查 llama-server 安装:"
    echo "  which llama-server"
    echo "  llama-server --version"
fi
