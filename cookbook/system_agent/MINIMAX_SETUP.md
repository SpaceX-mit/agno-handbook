# MiniMax.cn 使用步骤详解

## 第一步：注册并获取 API 密钥

### 1.1 访问 MiniMax 平台

打开浏览器访问：**https://platform.minimax.io/**

### 1.2 注册账号

1. 点击右上角"注册"或"登录"按钮
2. 可以使用以下方式注册：
   - 手机号注册（推荐）
   - 邮箱注册
   - 第三方账号（微信/GitHub等）

3. 完成注册后登录平台

### 1.3 获取 API 密钥

1. 登录后，进入控制台
2. 在左侧菜单找到 **"API 密钥"** 或 **"密钥管理"**
3. 点击 **"创建新密钥"**
4. 给密钥起个名字（例如：worker-system-agent）
5. **复制并保存 API 密钥**（只显示一次！）

示例密钥格式：
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 1.4 查看余额和配额

1. 在控制台查看账户余额
2. 新用户通常有免费额度
3. 确认可用的模型列表

## 第二步：在本地配置 API 密钥

### 2.1 临时设置（当前会话有效）

```bash
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### 2.2 永久设置（推荐）

**方式一：添加到 ~/.bashrc**

```bash
# 编辑配置文件
nano ~/.bashrc

# 在文件末尾添加
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 保存并退出（Ctrl+X，然后Y，然后Enter）

# 重新加载配置
source ~/.bashrc

# 验证设置
echo $MINIMAX_API_KEY
```

**方式二：添加到 ~/.bash_profile**

```bash
echo 'export MINIMAX_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.bash_profile
source ~/.bash_profile
```

**方式三：创建 .env 文件（适用于项目级配置）**

```bash
# 在项目目录创建 .env 文件
cd /home/bianbu/agno-riscv64
nano .env

# 添加以下内容
MINIMAX_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 保存退出
```

然后在代码中加载：
```python
from dotenv import load_dotenv
load_dotenv()
```

## 第三步：验证 API 连接

### 3.1 使用 curl 测试

```bash
curl -X POST https://api.minimax.io/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -d '{
    "model": "MiniMax-M3",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

成功响应示例：
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "你好！我是MiniMax..."
      }
    }
  ]
}
```

### 3.2 使用 Python 测试

创建测试脚本 `test_minimax.py`：

```python
#!/usr/bin/env python3
import os
from agno.models.minimax import MiniMax

# 检查 API 密钥
api_key = os.getenv('MINIMAX_API_KEY')
if not api_key:
    print("错误: MINIMAX_API_KEY 未设置")
    print("请运行: export MINIMAX_API_KEY='your-key'")
    exit(1)

print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
print("测试 MiniMax 连接...")

# 创建模型
model = MiniMax(id="MiniMax-M3")

# 测试简单对话
from agno.agent import Agent

agent = Agent(
    model=model,
    instructions="你是一个友好的助手。"
)

print("\n发送测试消息...")
response = agent.run("你好，请介绍一下你自己")
print(f"\n响应: {response.content}\n")
print("✓ MiniMax 连接成功！")
```

运行测试：
```bash
cd /home/bianbu/agno-riscv64
source .venv/bin/activate
python test_minimax.py
```

## 第四步：配置 Worker System Agent 使用 MiniMax

### 4.1 使用配置文件方式

```bash
cd /home/bianbu/agno-riscv64
source .venv/bin/activate

# 确认 API 密钥已设置
echo $MINIMAX_API_KEY

# 运行 agent（默认使用 MiniMax）
python cookbook/system_agent/worker_agent_minimax_llama.py
```

### 4.2 使用交互式 CLI

```bash
python cookbook/system_agent/cli_with_llm.py --model minimax
```

启动后会显示：
```
======================================================================
  Worker System Agent - AI 系统管理员
======================================================================

当前模型: MINIMAX

使用自然语言输入命令。示例:
  - 检查系统健康状态
  - 列出占用内存最多的5个进程
  - 显示磁盘空间
  - 查找所有Python文件

命令: 'exit', 'quit', 'bye' 退出 | 'clear' 清屏
======================================================================

Agent 就绪。输入你的命令:

你: 
```

### 4.3 修改代码选择模型

编辑 `worker_agent_minimax_llama.py`：

```python
# 找到这一行
selected_model = minimax_model  # 使用 MiniMax

# 确保这行被选中，其他被注释
# selected_model = ollama_model
# selected_model = worker_llama_model
```

## 第五步：实际使用示例

### 5.1 系统监控

```bash
你: 检查系统健康状态 - CPU、内存和磁盘使用情况
```

Agent 会调用 SystemMonitorTools 并返回结果。

### 5.2 文件操作

```bash
你: 列出 cookbook/system_agent 目录下的所有Python文件
```

### 5.3 进程管理

```bash
你: 显示占用内存最多的10个进程
```

### 5.4 包管理

```bash
你: 检查 docker 是否已安装
```

如果需要安装：
```bash
你: 安装 htop

Agent: 我将使用apt安装htop...
----------------------------------------------------------------------
需要确认
----------------------------------------------------------------------

工具: install_package
参数: {'name': 'htop'}

批准此操作? [y/N]: y
✓ 已批准
----------------------------------------------------------------------

Agent: 成功安装 htop
```

## 第六步：在 Worker 机器上部署

### 6.1 提交代码

在本地机器：
```bash
cd /data/workspace2026-new/work0618/tech-analyais0713/agno-handbook

# 添加新文件
git add cookbook/system_agent/worker_agent_minimax_llama.py
git add cookbook/system_agent/cli_with_llm.py
git add cookbook/system_agent/LLM_CONFIG.md

# 提交
git commit -m "feat: add MiniMax and local Llama support for system agent"

# 推送
git push origin main
```

### 6.2 在 Worker 机器上更新

```bash
# SSH 到 worker 机器
ssh bianbu@10.0.90.243

# 进入项目目录
cd /home/bianbu/agno-riscv64

# 拉取最新代码
git pull

# 激活虚拟环境
source .venv/bin/activate

# 设置 API 密钥
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 或永久设置
echo 'export MINIMAX_API_KEY="sk-xxx..."' >> ~/.bashrc
source ~/.bashrc
```

### 6.3 运行 Agent

```bash
# 方式1: 直接运行
python cookbook/system_agent/worker_agent_minimax_llama.py

# 方式2: 交互式 CLI
python cookbook/system_agent/cli_with_llm.py --model minimax

# 方式3: 运行示例
python cookbook/system_agent/examples.py 1
```

## 常见问题排查

### 问题1: API 密钥未设置

**错误信息**：
```
⚠️  警告: MINIMAX_API_KEY 未设置
请运行: export MINIMAX_API_KEY='your-key'
```

**解决方案**：
```bash
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### 问题2: API 密钥无效

**错误信息**：
```
ModelAuthenticationError: Invalid API key
```

**解决方案**：
1. 检查密钥是否正确复制（没有多余空格）
2. 在 MiniMax 平台验证密钥状态
3. 确认密钥没有过期或被撤销
4. 重新生成新密钥

### 问题3: 网络连接失败

**错误信息**：
```
Connection timeout or refused
```

**解决方案**：
```bash
# 检查网络连接
ping api.minimax.io

# 检查防火墙设置
curl https://api.minimax.io/v1/models

# 如果在公司网络，可能需要配置代理
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### 问题4: 余额不足

**错误信息**：
```
Insufficient balance or quota exceeded
```

**解决方案**：
1. 登录 MiniMax 平台查看余额
2. 充值或申请更多免费额度
3. 检查使用限制和配额

### 问题5: 响应超时

**解决方案**：
```python
# 增加超时时间
model = MiniMax(
    id="MiniMax-M3",
    timeout=60.0  # 增加到60秒
)
```

## 费用说明

### 免费额度

- 新用户通常有免费试用额度
- 具体额度查看平台说明
- 免费额度用完后需要充值

### 计费方式

- 按 Token 数量计费
- 不同模型价格不同
- 具体价格查看官方定价页面

### 成本优化建议

1. **使用合适的模型**：
   - 简单任务用较小模型
   - 复杂任务用 M3 模型

2. **控制上下文长度**：
   - 避免过长的对话历史
   - 定期清理不必要的上下文

3. **批量处理**：
   - 合并相关查询
   - 减少 API 调用次数

4. **监控使用量**：
   - 定期检查余额
   - 设置使用预警

## 完整示例脚本

保存为 `run_minimax_agent.sh`：

```bash
#!/bin/bash

# 设置 API 密钥
export MINIMAX_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 进入项目目录
cd /home/bianbu/agno-riscv64

# 激活虚拟环境
source .venv/bin/activate

# 运行 agent
python cookbook/system_agent/cli_with_llm.py --model minimax
```

使用：
```bash
chmod +x run_minimax_agent.sh
./run_minimax_agent.sh
```

## 下一步

1. ✅ 完成 API 密钥配置
2. ✅ 验证连接成功
3. ✅ 在 worker 机器上部署
4. ✅ 开始使用系统管理功能

现在你可以通过自然语言命令管理 worker 系统了！
