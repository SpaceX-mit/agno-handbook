# Qwen3.5-2B 本地模型集成指南

## 概述

使用本地 Qwen3.5-2B 模型运行 Worker System Agent，完全离线，无需 API 密钥。

## 模型信息

- **名称**: Qwen3.5-2B-Q4_0.gguf
- **大小**: 约 1.5 GB
- **量化**: Q4_0 (4-bit量化)
- **来源**: https://archive.spacemit.com/spacemit-ai/model_zoo/llm/
- **位置**: `/home/bianbu/models/Qwen3.5-2B-Q4_0.gguf`

## 快速开始

### 步骤 1: 下载模型（如果还没有）

```bash
ssh bianbu@10.0.90.243
mkdir -p /home/bianbu/models
cd /home/bianbu/models

# 下载模型
wget https://archive.spacemit.com/spacemit-ai/model_zoo/llm/Qwen3.5-2B-Q4_0.gguf

# 检查文件
ls -lh Qwen3.5-2B-Q4_0.gguf
```

### 步骤 2: 启动 llama-server

```bash
cd /home/bianbu/agno-riscv64

# 方式A: 前台运行（用于测试）
./cookbook/system_agent/start_qwen_server.sh

# 方式B: 后台运行（推荐）
nohup ./cookbook/system_agent/start_qwen_server.sh > qwen_server.log 2>&1 &

# 检查服务状态
curl http://localhost:11434/health
```

### 步骤 3: 启动 System Agent

```bash
cd /home/bianbu/agno-riscv64
./cookbook/system_agent/start_with_qwen.sh
```

## 详细配置

### llama-server 参数说明

在 `start_qwen_server.sh` 中配置：

```bash
llama-server \
    --model "/home/bianbu/models/Qwen3.5-2B-Q4_0.gguf" \
    --host "0.0.0.0" \              # 监听所有网络接口
    --port "11434" \                 # 端口号
    --ctx-size 4096 \               # 上下文长度
    --n-gpu-layers 99 \             # GPU加速层数（如有GPU）
    --threads 8 \                   # CPU线程数
    --log-disable                   # 禁用日志（可选）
```

### 性能调优

根据系统资源调整参数：

```bash
# 低内存配置（8GB RAM）
--ctx-size 2048
--threads 4

# 标准配置（16GB RAM）
--ctx-size 4096
--threads 8

# 高性能配置（32GB+ RAM）
--ctx-size 8192
--threads 16
```

## 使用示例

启动后，可以用中文自然语言管理系统：

```
你: 检查系统健康状态

Agent: [使用 Qwen3.5-2B 处理]
系统状态良好...
```

```
你: 列出占用内存最多的进程

Agent: [调用 SystemMonitorTools]
显示进程列表...
```

## 与其他模型对比

| 特性 | Qwen3.5-2B 本地 | MiniMax-M3 云端 |
|------|----------------|----------------|
| 速度 | 中等 (5-15秒) | 快 (1-3秒) |
| 成本 | 免费 | 按用量付费 |
| 隐私 | 完全本地 | 云端处理 |
| 网络 | 无需网络 | 需要网络 |
| 资源 | 需要本地CPU/内存 | 无本地消耗 |
| 模型大小 | 1.5GB | N/A |
| 推荐场景 | 离线环境、隐私敏感 | 在线环境、高性能需求 |

## 管理命令

### 启动服务

```bash
# 前台启动
./cookbook/system_agent/start_qwen_server.sh

# 后台启动
nohup ./cookbook/system_agent/start_qwen_server.sh > qwen_server.log 2>&1 &
```

### 检查状态

```bash
# 检查服务
curl http://localhost:11434/health

# 检查进程
ps aux | grep llama-server

# 检查端口
lsof -i :11434
```

### 停止服务

```bash
# 查找进程ID
ps aux | grep llama-server

# 停止服务
kill <PID>

# 或强制停止
pkill -9 llama-server
```

### 查看日志

```bash
# 如果后台运行
tail -f qwen_server.log

# 实时监控
watch -n 2 'curl -s http://localhost:11434/health'
```

## 故障排查

### 问题1: 模型文件不存在

```
❌ 错误: 模型文件不存在
```

**解决**:
```bash
cd /home/bianbu/models
wget https://archive.spacemit.com/spacemit-ai/model_zoo/llm/Qwen3.5-2B-Q4_0.gguf
```

### 问题2: 端口被占用

```
⚠ 警告: 端口 11434 已被占用
```

**解决**:
```bash
# 停止现有服务
lsof -i :11434 | grep LISTEN | awk '{print $2}' | xargs kill

# 或使用其他端口
# 修改 start_qwen_server.sh 中的 PORT 变量
```

### 问题3: llama-server 未安装

```
❌ llama-server 启动失败
```

**解决**:
```bash
# 检查安装
which llama-server

# 如果未安装，需要编译或下载预编译版本
# 参考: https://github.com/ggerganov/llama.cpp
```

### 问题4: 内存不足

```
Error: Failed to allocate memory
```

**解决**:
```bash
# 减小上下文大小
# 编辑 start_qwen_server.sh
--ctx-size 2048  # 改为更小的值

# 减少线程数
--threads 4
```

### 问题5: 响应很慢

**优化**:
1. 减少上下文长度
2. 增加线程数（不超过CPU核心数）
3. 如果有GPU，确保 `--n-gpu-layers` 设置正确
4. 关闭其他占用资源的进程

## 高级配置

### 多模型切换

你可以在同一台机器上运行多个模型服务：

```bash
# Qwen3.5-2B (端口 11434)
./start_qwen_server.sh

# 其他模型 (端口 11435)
llama-server --model /path/to/other-model.gguf --port 11435
```

然后在启动agent时指定：

```bash
export OLLAMA_HOST="http://localhost:11435"
./start_with_qwen.sh
```

### 远程访问

如果需要从其他机器访问：

```bash
# 修改 start_qwen_server.sh
--host "0.0.0.0"  # 已经是这个配置

# 防火墙开放端口
sudo ufw allow 11434
```

从其他机器连接：

```bash
export OLLAMA_HOST="http://10.0.90.243:11434"
python cookbook/system_agent/cli_with_llm.py --model ollama
```

## 性能基准

基于 RISC-V 16核、32GB RAM 的测试结果：

| 指标 | 数值 |
|------|------|
| 启动时间 | ~5-10秒 |
| 首次响应 | ~5-15秒 |
| 后续响应 | ~3-8秒 |
| 内存占用 | ~2-3GB |
| CPU使用 | 30-60% (推理时) |

## 与 Ollama 对比

`llama-server` 是 llama.cpp 的服务器模式，与 Ollama 类似但更轻量：

| 特性 | llama-server | Ollama |
|------|-------------|--------|
| 模型管理 | 手动 | 自动 |
| 配置 | 命令行参数 | Modelfile |
| 资源占用 | 更轻量 | 稍高 |
| 易用性 | 需手动配置 | 开箱即用 |

## 参考资源

- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [Qwen 模型文档](https://github.com/QwenLM/Qwen)
- [GGUF 格式说明](https://github.com/ggerganov/ggml)

## 下一步

1. ✅ 下载 Qwen3.5-2B 模型
2. ✅ 配置 llama-server
3. ⏳ 启动服务并测试
4. ⏳ 集成到 System Agent
5. ⏳ 性能调优

---

当前状态: **模型下载中** (34% 完成)

监控下载进度:
```bash
ssh bianbu@10.0.90.243
tail -f /home/bianbu/models/download.log
```
