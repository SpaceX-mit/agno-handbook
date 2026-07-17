# 使用 MiniMax 和本地 Llama 配置指南

本指南说明如何配置 Worker System Agent 使用 MiniMax 云服务或本地 Llama 服务器。

## 支持的模型

### 1. MiniMax (云服务)
- **优点**: 功能强大、响应快速、无需本地资源
- **缺点**: 需要网络连接、API密钥、可能产生费用
- **适用场景**: 生产环境、需要最佳性能

### 2. Ollama/Llama (本地)
- **优点**: 完全离线、无API费用、数据隐私
- **缺点**: 需要本地GPU/CPU资源、响应较慢
- **适用场景**: 开发测试、隐私要求高、无网络环境

## 快速开始

### 方式一: 使用 MiniMax

```bash
# 1. 设置 API 密钥
export MINIMAX_API_KEY='your-minimax-api-key'

# 2. 运行 agent (使用配置文件)
cd /home/bianbu/agno-riscv64
source .venv/bin/activate
python cookbook/system_agent/worker_agent_minimax_llama.py

# 3. 或使用交互式 CLI
python cookbook/system_agent/cli_with_llm.py --model minimax
```

### 方式二: 使用本地 Ollama/Llama

```bash
# 1. 确保 llama-server 正在运行
# 检查服务状态
curl http://localhost:11434/api/tags

# 如果没有运行，启动它
# ollama serve

# 2. (可选) 设置自定义配置
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.1  # 或其他模型

# 3. 运行 agent
cd /home/bianbu/agno-riscv64
source .venv/bin/activate
python cookbook/system_agent/cli_with_llm.py --model ollama
```

### 方式三: 使用 Worker 机器上的 Llama

```bash
# 从其他机器连接到 worker 机器的 llama-server
python cookbook/system_agent/cli_with_llm.py --model worker-llama
```

## 详细配置

### MiniMax 配置

#### 1. 获取 API 密钥

访问 [MiniMax 平台](https://platform.minimax.io/) 注册并获取 API 密钥。

#### 2. 配置环境变量

```bash
# 临时设置 (当前会话)
export MINIMAX_API_KEY='your-key-here'

# 永久设置 (添加到 ~/.bashrc)
echo 'export MINIMAX_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. 可用模型

```python
from agno.models.minimax import MiniMax

# MiniMax-M3 (推荐)
model = MiniMax(id="MiniMax-M3")

# MiniMax-M2.5
model = MiniMax(id="MiniMax-M2.5")
```

#### 4. 自定义配置

```python
model = MiniMax(
    id="MiniMax-M3",
    base_url="https://api.minimax.io/v1",  # 自定义端点
    timeout=30.0,  # 超时设置
    max_retries=3,  # 重试次数
)
```

### Ollama/Llama 配置

#### 1. 安装 Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# 或使用包管理器
# Ubuntu/Debian
# wget https://ollama.com/download/ollama-linux-amd64.tgz

# 验证安装
ollama --version
```

#### 2. 下载模型

```bash
# Llama 3.1 (推荐)
ollama pull llama3.1

# Llama 3.2
ollama pull llama3.2

# Qwen 2.5
ollama pull qwen2.5

# 查看已下载的模型
ollama list
```

#### 3. 启动服务

```bash
# 前台运行
ollama serve

# 后台运行 (使用 systemd)
sudo systemctl enable ollama
sudo systemctl start ollama

# 检查状态
sudo systemctl status ollama
```

#### 4. 配置环境变量

```bash
# Ollama 服务地址
export OLLAMA_HOST=http://localhost:11434

# 使用的模型
export OLLAMA_MODEL=llama3.1

# Worker 机器地址 (如果 llama-server 在 worker 上)
export OLLAMA_HOST=http://10.0.90.243:11434
```

#### 5. 验证连接

```bash
# 测试 API
curl http://localhost:11434/api/tags

# 测试生成
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

#### 6. Python 配置

```python
from agno.models.ollama import Ollama

# 本地 Ollama
model = Ollama(
    id="llama3.1",
    host="http://localhost:11434",
)

# Worker 机器上的 Ollama
model = Ollama(
    id="llama3.1",
    host="http://10.0.90.243:11434",
)

# 自定义配置
model = Ollama(
    id="llama3.1",
    host="http://localhost:11434",
    timeout=60.0,
    options={
        "temperature": 0.7,
        "top_p": 0.9,
    }
)
```

## 在 Worker 机器上部署

### 1. 在 Worker 机器上启动 Llama

```bash
# SSH 到 worker 机器
ssh bianbu@10.0.90.243

# 安装 Ollama (如果还没有)
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull llama3.1

# 启动服务
ollama serve
# 或使用 systemd
sudo systemctl start ollama
```

### 2. 部署更新的代码

```bash
# 在本地机器上提交代码
git add cookbook/system_agent/
git commit -m "feat: add MiniMax and local Llama support"
git push origin main

# 在 worker 机器上更新
ssh bianbu@10.0.90.243
cd /home/bianbu/agno-riscv64
git pull
source .venv/bin/activate
```

### 3. 运行 Agent

```bash
# 使用本地 Llama
python cookbook/system_agent/cli_with_llm.py --model ollama

# 使用 MiniMax
export MINIMAX_API_KEY='your-key'
python cookbook/system_agent/cli_with_llm.py --model minimax
```

## 使用示例

### 交互式 CLI

```bash
# 启动 CLI
python cookbook/system_agent/cli_with_llm.py --model ollama

# 在 CLI 中输入命令
你: 检查系统健康状态
Agent: [显示 CPU、内存、磁盘信息]

你: 列出占用内存最多的5个进程
Agent: [显示进程列表]

你: 安装 htop
Agent: [请求确认]
批准此操作? [y/N]: y
Agent: [执行安装]
```

### 编程方式

```python
from cookbook.system_agent.worker_agent_minimax_llama import worker_system_agent

# 运行查询
response = worker_system_agent.run("检查系统健康状态")
print(response.content)

# 流式响应
worker_system_agent.print_response(
    "显示磁盘空间和内存使用情况",
    stream=True
)
```

## 性能对比

| 模型 | 响应速度 | 资源消耗 | 成本 | 隐私 |
|------|---------|---------|------|------|
| MiniMax-M3 | 快 (1-3s) | 无 (云端) | 按用量 | 云端处理 |
| Llama3.1 (本地) | 中 (5-15s) | 高 (GPU/CPU) | 无 | 完全本地 |
| Llama3.2 (本地) | 快 (3-8s) | 中 (更小模型) | 无 | 完全本地 |

## 故障排查

### MiniMax 问题

**问题**: `MINIMAX_API_KEY not set`
```bash
# 解决: 设置环境变量
export MINIMAX_API_KEY='your-key'
```

**问题**: `Connection timeout`
```bash
# 解决: 检查网络连接和防火墙
curl https://api.minimax.io/v1/models
```

**问题**: `Authentication failed`
```bash
# 解决: 验证 API 密钥是否正确
echo $MINIMAX_API_KEY
```

### Ollama 问题

**问题**: `Connection refused to localhost:11434`
```bash
# 解决: 启动 Ollama 服务
ollama serve
# 或
sudo systemctl start ollama
```

**问题**: `Model not found`
```bash
# 解决: 拉取模型
ollama pull llama3.1
ollama list  # 查看已有模型
```

**问题**: `Out of memory`
```bash
# 解决: 使用更小的模型或增加系统内存
ollama pull llama3.2  # 更小的模型
```

**问题**: 响应很慢
```bash
# 解决: 
# 1. 检查 CPU/GPU 使用率
top
nvidia-smi  # 如果有 GPU

# 2. 使用更小的模型
ollama pull llama3.2

# 3. 调整并发设置
export OLLAMA_NUM_PARALLEL=2
```

## 高级配置

### 模型切换

在代码中动态切换模型：

```python
import os

# 根据环境变量选择模型
model_type = os.getenv("AGENT_MODEL", "ollama")

if model_type == "minimax":
    model = MiniMax(id="MiniMax-M3")
elif model_type == "ollama":
    model = Ollama(id="llama3.1")

agent = Agent(model=model, ...)
```

### Fallback 配置

配置主模型失败时的备用模型：

```python
from agno.models.fallback import FallbackConfig

agent = Agent(
    model=MiniMax(id="MiniMax-M3"),
    fallback_models=[
        Ollama(id="llama3.1", host="http://localhost:11434"),
    ],
    fallback_config=FallbackConfig(
        max_retries=2,
        retry_delay=1.0,
    )
)
```

## 参考资料

- [MiniMax 文档](https://platform.minimax.io/docs)
- [Ollama 文档](https://ollama.com/docs)
- [Agno 模型配置](https://docs.agno.com/models)
- [Worker System Agent README](./README.md)
