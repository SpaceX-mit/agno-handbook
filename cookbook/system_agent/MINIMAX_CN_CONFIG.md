# MiniMax CN (minimaxi.com) 快速配置指南

## 你的配置信息

```bash
export MINIMAX_API_KEY="sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
export MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
export MINIMAX_MODEL="abab6.5s-chat"
```

## 快速开始

### 方式一：使用一键启动脚本（最简单）

```bash
cd /home/bianbu/agno-riscv64
./cookbook/system_agent/start_minimax_cn.sh
```

这个脚本会：
1. 自动设置你的API密钥和端点
2. 测试连接
3. 启动系统agent

### 方式二：手动配置

```bash
# 1. 设置环境变量
export MINIMAX_API_KEY="sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
export MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
export MINIMAX_MODEL="abab6.5s-chat"

# 2. 进入项目目录
cd /home/bianbu/agno-riscv64

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 启动agent
python cookbook/system_agent/cli_with_llm.py --model minimax
```

## 永久配置（推荐）

将配置添加到 `~/.bashrc`：

```bash
cat >> ~/.bashrc << 'EOF'

# MiniMax CN 配置
export MINIMAX_API_KEY="sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
export MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
export MINIMAX_MODEL="abab6.5s-chat"
EOF

# 重新加载配置
source ~/.bashrc
```

之后每次打开终端都会自动设置好，直接运行即可：

```bash
cd /home/bianbu/agno-riscv64
python cookbook/system_agent/cli_with_llm.py --model minimax
```

## 测试连接

```bash
cd /home/bianbu/agno-riscv64
source .venv/bin/activate

# 使用修改后的测试脚本
python cookbook/system_agent/test_minimax.py
```

或手动测试：

```bash
curl -X POST https://api.minimaxi.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0" \
  -d '{
    "model": "abab6.5s-chat",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 可用模型

MiniMax CN 支持的模型：

| 模型名 | 描述 | 推荐场景 |
|--------|------|----------|
| `abab6.5s-chat` | 最新快速模型 | 日常对话、系统管理 |
| `abab6.5-chat` | 标准模型 | 通用场景 |
| `abab5.5-chat` | 经济型模型 | 简单任务 |

切换模型：

```bash
export MINIMAX_MODEL="abab6.5-chat"  # 使用标准模型
export MINIMAX_MODEL="abab5.5-chat"  # 使用经济型
```

## 在 Worker 机器上部署

### 1. SSH 到 worker

```bash
ssh bianbu@10.0.90.243
```

### 2. 更新代码

```bash
cd /home/bianbu/agno-riscv64
git pull
```

### 3. 配置并运行

```bash
# 方式A: 使用一键脚本
./cookbook/system_agent/start_minimax_cn.sh

# 方式B: 手动配置
export MINIMAX_API_KEY="sk-cp-vkEj751v_1aMyUXzNAkeaXw90HnTQ8GbQubW85hBWHxHrR1PaRX-S_DVVWzDCpaVLhbJHxjzTBH7lv2pXmoWhyI5pyM9wevrFr3ggQBOfi73PaTfydZUpa0"
export MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
python cookbook/system_agent/cli_with_llm.py --model minimax
```

## 使用示例

启动agent后：

```
你: 检查系统健康状态

Agent: 正在检查系统状态...
[显示CPU、内存、磁盘信息]
```

```
你: 列出占用内存最多的5个进程

Agent: 
PID     名称                CPU%    内存%   内存(MB)
--------------------------------------------------------
3598510 llama-server        0.0     6.5     2099.0
3666364 python3             0.0     3.6     1140.8
...
```

## 故障排查

### 问题1：连接超时

```bash
# 检查网络
ping api.minimaxi.com

# 测试端点
curl https://api.minimaxi.com/v1
```

### 问题2：认证失败

```bash
# 检查密钥是否正确设置
echo $MINIMAX_API_KEY

# 验证密钥格式（应该以 sk-cp- 开头）
```

### 问题3：模型不存在

```bash
# 使用推荐的模型
export MINIMAX_MODEL="abab6.5s-chat"
```

## 注意事项

1. **API密钥安全**：不要将密钥提交到公开的git仓库
2. **费用控制**：定期检查API使用量和余额
3. **网络要求**：确保能访问 `api.minimaxi.com`
4. **模型选择**：根据任务复杂度选择合适的模型

## 与国际版的区别

| 特性 | 国际版 (minimax.io) | 国内版 (minimaxi.com) |
|------|---------------------|----------------------|
| 端点 | api.minimax.io | api.minimaxi.com |
| 模型 | MiniMax-M3 | abab6.5s-chat |
| 网络 | 国际网络 | 国内网络更快 |
| 密钥格式 | sk-xxx | sk-cp-xxx |

你的配置使用的是**国内版**，访问速度更快！

## 下一步

✅ 配置已设置  
✅ 连接已测试  
✅ 可以开始使用

现在运行：
```bash
./cookbook/system_agent/start_minimax_cn.sh
```

开始用自然语言管理你的系统吧！🚀
