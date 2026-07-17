#!/bin/bash
# 快速启动脚本 - 使用本地 Ollama/Llama

set -e

echo "========================================================================"
echo "  Worker System Agent - Ollama/Llama 快速启动"
echo "========================================================================"
echo

# 配置
OLLAMA_HOST=${OLLAMA_HOST:-http://localhost:11434}
OLLAMA_MODEL=${OLLAMA_MODEL:-llama3.1}

echo "Ollama 配置:"
echo "  主机: $OLLAMA_HOST"
echo "  模型: $OLLAMA_MODEL"
echo

# 检查 Ollama 服务
echo "检查 Ollama 服务..."
if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
    echo "✓ Ollama 服务运行正常"
else
    echo "❌ 错误: 无法连接到 Ollama 服务 ($OLLAMA_HOST)"
    echo
    echo "请确保 Ollama 正在运行:"
    echo "  ollama serve"
    echo
    echo "或启动服务:"
    echo "  sudo systemctl start ollama"
    echo
    exit 1
fi
echo

# 检查模型是否存在
echo "检查模型 $OLLAMA_MODEL..."
if curl -s "$OLLAMA_HOST/api/tags" | grep -q "\"name\":\"$OLLAMA_MODEL\""; then
    echo "✓ 模型 $OLLAMA_MODEL 已安装"
else
    echo "⚠ 警告: 模型 $OLLAMA_MODEL 未安装"
    echo
    echo "请运行以下命令安装:"
    echo "  ollama pull $OLLAMA_MODEL"
    echo
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
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

# 检查依赖
echo "检查依赖..."
if ! python -c "from agno.models.ollama import Ollama" 2>/dev/null; then
    echo "安装缺失的依赖..."
    pip install -e libs/agno > /dev/null
    pip install ollama > /dev/null
fi
echo "✓ 依赖检查完成"
echo

# 运行 agent
echo "========================================================================"
echo "启动 Worker System Agent (使用 Ollama/$OLLAMA_MODEL)"
echo "========================================================================"
echo

export OLLAMA_HOST
export OLLAMA_MODEL
python cookbook/system_agent/cli_with_llm.py --model ollama
