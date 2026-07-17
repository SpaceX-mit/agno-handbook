#!/bin/bash
# 快速启动脚本 - 使用 MiniMax

set -e

echo "========================================================================"
echo "  Worker System Agent - MiniMax 快速启动"
echo "========================================================================"
echo

# 检查 API 密钥
if [ -z "$MINIMAX_API_KEY" ]; then
    echo "❌ 错误: MINIMAX_API_KEY 未设置"
    echo
    echo "请先设置 API 密钥:"
    echo "  export MINIMAX_API_KEY='your-key-here'"
    echo
    echo "或永久设置:"
    echo "  echo 'export MINIMAX_API_KEY=\"your-key\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo
    exit 1
fi

echo "✓ API 密钥已设置: ${MINIMAX_API_KEY:0:10}...${MINIMAX_API_KEY: -5}"
echo

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    echo "请运行: ./scripts/dev_setup.sh"
    exit 1
fi

echo "✓ 虚拟环境存在"
echo

# 激活虚拟环境
source .venv/bin/activate
echo "✓ 虚拟环境已激活"
echo

# 检查依赖
echo "检查依赖..."
if ! python -c "from agno.models.minimax import MiniMax" 2>/dev/null; then
    echo "安装缺失的依赖..."
    pip install -e libs/agno > /dev/null
fi
echo "✓ 依赖检查完成"
echo

# 运行 agent
echo "========================================================================"
echo "启动 Worker System Agent (使用 MiniMax)"
echo "========================================================================"
echo

python cookbook/system_agent/cli_with_llm.py --model minimax
