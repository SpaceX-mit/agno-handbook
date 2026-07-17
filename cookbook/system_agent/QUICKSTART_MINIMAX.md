# 🚀 MiniMax 快速使用指南

## 📋 一分钟快速开始

```bash
# 1. 设置 API 密钥
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 2. 启动 agent
cd /home/bianbu/agno-riscv64
./cookbook/system_agent/start_minimax.sh
```

就这么简单！

---

## 📝 详细步骤

### 步骤 1: 获取 API 密钥

1. 访问 https://platform.minimax.io/
2. 注册/登录账号
3. 进入"API 密钥"页面
4. 创建新密钥
5. **复制并保存**密钥（只显示一次）

### 步骤 2: 配置密钥

**方式 A - 临时设置**（推荐测试用）
```bash
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

**方式 B - 永久设置**（推荐生产用）
```bash
echo 'export MINIMAX_API_KEY="sk-xxx..."' >> ~/.bashrc
source ~/.bashrc
```

### 步骤 3: 测试连接

```bash
cd /home/bianbu/agno-riscv64
source .venv/bin/activate
python cookbook/system_agent/test_minimax.py
```

看到 `✓ 测试成功！` 就可以继续了。

### 步骤 4: 启动 Agent

**方式 A - 使用启动脚本**（最简单）
```bash
./cookbook/system_agent/start_minimax.sh
```

**方式 B - 使用 CLI**
```bash
python cookbook/system_agent/cli_with_llm.py --model minimax
```

**方式 C - 直接运行**
```bash
python cookbook/system_agent/worker_agent_minimax_llama.py
```

---

## 💡 使用示例

启动后，你可以用自然语言命令管理系统：

```
你: 检查系统健康状态

Agent: [显示 CPU、内存、磁盘使用情况]
```

```
你: 列出占用内存最多的5个进程

Agent: 
PID    NAME              CPU%   MEM%   MEM(MB)
------------------------------------------------
3598510 llama-server     0.0    6.5    2099.0
3666364 python3          0.0    3.6    1140.8
...
```

```
你: 查找所有 Python 文件

Agent: [使用 FileTools 搜索并列出文件]
```

```
你: 安装 htop

Agent: 我将安装 htop 包...
----------------------------------------------------------------------
需要确认
----------------------------------------------------------------------
工具: install_package
参数: {'name': 'htop'}

批准此操作? [y/N]: y

Agent: ✓ 成功安装 htop
```

---

## 🔧 在 Worker 机器上部署

### 1. 更新代码

```bash
# SSH 到 worker
ssh bianbu@10.0.90.243

# 更新仓库
cd /home/bianbu/agno-riscv64
git pull

# 激活环境
source .venv/bin/activate
```

### 2. 设置密钥

```bash
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 或永久设置
echo 'export MINIMAX_API_KEY="sk-xxx..."' >> ~/.bashrc
source ~/.bashrc
```

### 3. 运行

```bash
# 测试连接
python cookbook/system_agent/test_minimax.py

# 启动 agent
./cookbook/system_agent/start_minimax.sh
```

---

## 🆚 MiniMax vs Ollama 对比

| 特性 | MiniMax | Ollama (本地 Llama) |
|------|---------|---------------------|
| 速度 | ⚡ 快 (1-3秒) | 🐢 中 (5-15秒) |
| 成本 | 💰 按用量付费 | 🆓 免费 |
| 隐私 | ☁️ 云端处理 | 🔒 完全本地 |
| 网络 | 🌐 需要网络 | ❌ 无需网络 |
| 资源 | 💻 无本地消耗 | 🖥️ 需要 GPU/CPU |
| 推荐场景 | 生产环境 | 开发测试 |

---

## ❓ 常见问题

### Q1: 如何切换模型？

**使用 MiniMax:**
```bash
python cookbook/system_agent/cli_with_llm.py --model minimax
```

**使用 Ollama:**
```bash
python cookbook/system_agent/cli_with_llm.py --model ollama
```

### Q2: API 密钥在哪里找？

登录 https://platform.minimax.io/ → API 密钥 → 创建新密钥

### Q3: 如何检查余额？

登录 MiniMax 平台 → 控制台 → 账户余额

### Q4: 连接失败怎么办？

```bash
# 1. 检查密钥
echo $MINIMAX_API_KEY

# 2. 测试网络
curl https://api.minimax.io/v1/models

# 3. 运行测试脚本
python cookbook/system_agent/test_minimax.py
```

### Q5: 如何节省费用？

1. 使用简短清晰的命令
2. 避免重复相同的查询
3. 开发测试时使用本地 Ollama
4. 生产环境才使用 MiniMax

---

## 📚 更多文档

- **完整配置指南**: `cookbook/system_agent/LLM_CONFIG.md`
- **详细设置步骤**: `cookbook/system_agent/MINIMAX_SETUP.md`
- **系统 Agent 文档**: `cookbook/system_agent/README.md`

---

## 🎯 下一步

✅ 获取 MiniMax API 密钥  
✅ 配置环境变量  
✅ 测试连接  
✅ 启动 Agent  
✅ 开始使用！

现在你可以用自然语言管理 worker 系统了！🎉
