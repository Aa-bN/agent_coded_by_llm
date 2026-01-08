# Agent Coded By LLM

### 由大模型实现的ReAct智能体。 A ReAct Agent Coded By an LLM.

## 目录

1. [项目概述](#1-项目概述)
2. [环境要求](#2-环境要求)
3. [安装指南](#3-安装指南)
4. [快速开始](#4-快速开始)
5. [核心概念](#5-核心概念)
6. [模块详解](#6-模块详解)
7. [工具开发指南](#7-工具开发指南)
8. [高级配置](#8-高级配置)
9. [API 参考](#9-api-参考)
10. [常见问题](#10-常见问题)
11. [最佳实践](#11-最佳实践)

---

## 1. 项目概述

### 1.1 什么是 ReAct Agent？

ReAct（Reasoning + Acting）是一种将推理和行动相结合的 Agent 模式。本项目实现了一个基于 ReAct 模式的智能代理，能够：

- **思考（Thought）**：分析用户问题，制定解决方案
- **行动（Action）**：调用外部工具获取信息或执行操作
- **观察（Observation）**：接收工具返回的结果
- **循环迭代**：根据观察结果继续推理，直到得出最终答案

### 1.2 核心特性

| 特性 | 描述 |
|------|------|
| 🔄 ReAct 模式 | 标准的 Thought-Action-Observation 循环 |
| 📦 模块化设计 | LLM、Tool、Agent 各模块独立，易于扩展 |
| 🌊 流式输出 | 支持实时流式响应，提升用户体验 |
| 🔧 灵活的工具注册 | 支持类继承和装饰器两种方式注册工具 |
| 🎯 DeepSeek 支持 | 开箱即用的 DeepSeek 模型支持 |
| 📝 详细日志 | 可配置的详细执行日志 |

### 1.3 项目结构

```
agent_coded_by_llm/
├── __init__.py          # 包入口，导出公共 API
├── llm/
│   ├── __init__.py
│   └── base.py          # LLM 封装模块
├── tools/
│   ├── __init__.py
│   ├── base.py          # 工具基类和注册器
│   └── builtin.py       # 内置工具集
├── agent/
│   ├── __init__.py
│   ├── react.py         # ReAct Agent 核心实现
│   └── prompt.py        # Prompt 模板
├── utils/
│   ├── __init__.py
│   └── parser.py        # LLM 输出解析器
├── main.py              # 程序入口
├── requirements.txt     # 依赖列表
└── .env.example         # 环境变量示例
```

---

## 2. 环境要求

### 2.1 系统要求

- **操作系统**：Windows / macOS / Linux
- **Python 版本**：Python 3.9+（推荐 3.10+）

### 2.2 依赖库

| 库名 | 版本要求 | 用途 |
|------|----------|------|
| `openai` | >=1.0.0 | OpenAI API 客户端（兼容 DeepSeek） |
| `python-dotenv` | >=1.0.0 | 环境变量管理 |

### 2.3 API 密钥

需要获取 DeepSeek API 密钥：
1. 访问 [DeepSeek 官网](https://platform.deepseek. com/)
2. 注册账号并创建 API Key
3. 记录 API Key 用于后续配置

---

## 3. 安装指南

### 3.1 克隆/下载项目

```bash
# 1.创建文件夹，作为PyCharm、VSCode等编辑器打开的项目根目录
mkdir react_agents
cd react_agents
# 2.git下载解压
  # 当前文件夹：react_agents(项目文件夹) - agent_coded_by_llm(包含1.3的项目结构)
```

### 3.2 创建虚拟环境（可选，推荐）

```bash
# conda/miniconda
```

### 3.3 安装依赖

```bash
pip install -r requirements. txt
```

### 3.4 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件
```

编辑 `.env` 文件内容：

```ini
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3.5 验证安装

```bash
python -c "from agent_coded_by_llm import ReActAgent; print('✅ 安装成功')"
```

---

## 4. 快速开始

### 4.1 最简示例

```python
from agent_coded_by_llm import (
    BaseLLM, LLMConfig, ReActAgent, 
    AgentConfig, register_builtin_tools, default_registry
)

# 1. 配置 LLM
llm_config = LLMConfig(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com",
    model="deepseek-chat"
)
llm = BaseLLM(llm_config)

# 2. 注册内置工具
register_builtin_tools()

# 3. 创建 Agent
agent = ReActAgent(llm=llm)

# 4. 运行查询
result = agent.run("计算 25 * 4 + 10 的结果")
print(f"答案: {result. final_answer}")
```

### 4.2 交互式模式

```bash
# 启动交互式对话
python -m agent_coded_by_llm.main
```

交互示例：

```
============================================================
🤖 ReAct Agent Interactive Mode
Type 'quit' or 'exit' to end the conversation
Type 'tools' to list available tools
============================================================

👤 You: 现在几点了？

🤖 Agent: 
=== Step 1 ===
Thinking:  Thought: 用户想知道当前时间，我需要使用 datetime 工具来获取。
Action: datetime
Action Input: {"format": "time"}

🔧 Calling tool: datetime
📊 Observation: Current time:  14:30:25

=== Step 2 ===
Thinking: Thought:  我已经获取到了当前时间，可以回答用户了。
Action: finish
Action Input: 现在的时间是 14:30:25。

📝 Final Answer:  现在的时间是 14:30:25。
```

### 4.3 流式输出模式

```python
# 流式模式运行
for output in agent.run_stream("帮我计算 100 / 4"):
    if output["type"] == "stream":
        print(output["content"], end="", flush=True)
    elif output["type"] == "answer":
        print(output["content"])
```

### 4.4 命令行单次查询

```bash
python -m agent_coded_by_llm.main "今天是几号？"
```

---

## 5. 核心概念

### 5.1 ReAct 循环

```
┌─────────────────────────────────────────────────────────────┐
│                      ReAct 执行流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   用户输入 ──▶ [Thought] ──▶ [Action] ──▶ [Observation]     │
│                    │              │              │          │
│                    │              │              │          │
│                    │              ▼              │          │
│                    │         执行工具            │          │
│                    │              │              │          │
│                    │              ▼              │          │
│                    │         获取结果            │          │
│                    │              │              │          │
│                    ◀──────────────┴──────────────┘          │
│                    │                                        │
│                    ▼                                        │
│              是否完成？                                      │
│              /      \                                       │
│            是        否                                      │
│            │          │                                     │
│            ▼          └──────▶ 继续循环                      │
│        输出答案                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 输出格式

Agent 的每次响应遵循以下格式：

```
Thought: [推理过程 - 分析问题，决定下一步行动]
Action: [工具名称 或 "finish"]
Action Input: [工具参数的 JSON 格式 或 最终答案]
```

### 5.3 动作类型

| 动作类型 | 说明 | 示例 |
|----------|------|------|
| `tool` | 调用指定工具 | `Action: calculator` |
| `finish` | 结束对话，输出答案 | `Action: finish` |
| `invalid` | 无效格式（会触发重试） | - |

---

## 6. 模块详解

### 6.1 LLM 模块 (`llm/base.py`)

#### LLMConfig - 配置类

```python
from agent_coded_by_llm import LLMConfig

config = LLMConfig(
    api_key="your-api-key",      # API 密钥（必填）
    base_url="https://api.deepseek.com",  # API 地址
    model="deepseek-chat",       # 模型名称
    temperature=0.7,             # 生成温度 (0-2)
    max_tokens=4096              # 最大输出 token 数
)
```

#### BaseLLM - LLM 封装类

```python
from agent_coded_by_llm import BaseLLM

llm = BaseLLM(config)

# 同步调用
response = llm.chat([
    {"role": "user", "content": "你好"}
])
print(response. content)

# 流式调用
for chunk in llm. chat([{"role": "user", "content": "你好"}], stream=True):
    print(chunk, end="")
```

### 6.2 Tool 模块 (`tools/base.py`)

#### ToolParameter - 参数定义

```python
from agent_coded_by_llm import ToolParameter

param = ToolParameter(
    name="query",           # 参数名
    type="string",          # 参数类型
    description="搜索关键词",  # 参数描述
    required=True,          # 是否必填
    default=None            # 默认值
)
```

#### ToolRegistry - 工具注册器

```python
from agent_coded_by_llm import ToolRegistry, default_registry

# 使用全局注册器
default_registry.register(my_tool)

# 或创建独立注册器
custom_registry = ToolRegistry()
custom_registry.register(my_tool)

# 获取工具
tool = custom_registry. get("tool_name")

# 执行工具
result = custom_registry.execute("tool_name", param1="value1")

# 获取所有工具描述
print(custom_registry. get_tools_prompt())
```

### 6.3 Agent 模块 (`agent/react.py`)

#### AgentConfig - Agent 配置

```python
from agent_coded_by_llm import AgentConfig

config = AgentConfig(
    max_iterations=10,  # 最大迭代次数（防止无限循环）
    verbose=True,       # 是否输出详细日志
    stream=True         # 是否使用流式输出
)
```

#### ReActAgent - 核心 Agent

```python
from agent_coded_by_llm import ReActAgent

agent = ReActAgent(
    llm=llm,                        # LLM 实例
    tool_registry=default_registry,  # 工具注册器
    config=agent_config             # Agent 配置
)

# 重置状态
agent.reset()

# 同步运行
result = agent.run("你的问题")

# 流式运行
for output in agent.run_stream("你的问题"):
    print(output)
```

#### AgentResult - 执行结果

```python
result = agent.run("问题")

print(result.success)         # 是否成功
print(result.final_answer)    # 最终答案
print(result.steps)           # 执行步骤列表
print(result.error)           # 错误信息（如有）
print(result.total_iterations)  # 总迭代次数
```

### 6.4 内置工具 (`tools/builtin. py`)

| 工具名称 | 功能 | 参数 |
|----------|------|------|
| `calculator` | 数学表达式计算 | `expression`: 数学表达式 |
| `datetime` | 获取日期时间 | `format`: date/time/datetime/timestamp |
| `wikipedia` | Wikipedia 搜索（模拟） | `query`: 搜索词 |
| `weather` | 天气查询（模拟） | `city`: 城市名 |

---

## 7. 工具开发指南

### 7.1 方式一：类继承（推荐用于复杂工具）

```python
from agent_coded_by_llm import BaseTool, ToolParameter, default_registry

class MyDatabaseTool(BaseTool):
    """数据库查询工具"""
    
    # 工具元信息
    name = "database"
    description = "Query the database for information"
    parameters = [
        ToolParameter(
            name="sql",
            type="string",
            description="SQL query to execute"
        ),
        ToolParameter(
            name="limit",
            type="integer",
            description="Maximum number of results",
            required=False,
            default=10
        )
    ]
    
    def __init__(self, connection_string: str):
        """可以在初始化时传入配置"""
        self.connection_string = connection_string
    
    def execute(self, sql: str, limit: int = 10) -> str:
        """
        执行工具逻辑
        
        Args:
            sql: SQL 查询语句
            limit: 结果限制
            
        Returns: 
            查询结果的字符串表示
        """
        # 实现你的逻辑
        # result = self.db. execute(sql, limit)
        return f"Query executed: {sql}, limit: {limit}"

# 注册工具
db_tool = MyDatabaseTool("postgresql://localhost/mydb")
default_registry.register(db_tool)
```

### 7.2 方式二：装饰器（推荐用于简单工具）

```python
from agent_coded_by_llm import tool, ToolParameter, default_registry

@tool(
    name="unit_convert",
    description="Convert values between different units",
    parameters=[
        ToolParameter("value", "number", "The value to convert"),
        ToolParameter("from_unit", "string", "Source unit"),
        ToolParameter("to_unit", "string", "Target unit")
    ]
)
def unit_converter(value: float, from_unit: str, to_unit:  str) -> str:
    """单位转换工具"""
    # 简化的转换逻辑
    conversions = {
        ("km", "m"): lambda x: x * 1000,
        ("m", "km"): lambda x: x / 1000,
        ("kg", "g"): lambda x: x * 1000,
        ("g", "kg"): lambda x: x / 1000,
    }
    
    key = (from_unit. lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result} {to_unit}"
    else:
        return f"Error: Cannot convert from {from_unit} to {to_unit}"

# 装饰器返回工具实例，直接注册
default_registry.register(unit_converter)
```

### 7.3 工具开发最佳实践

```python
class WellDesignedTool(BaseTool):
    """
    良好设计的工具示例
    
    遵循以下原则：
    1. 清晰的名称和描述
    2. 完整的参数定义
    3. 健壮的错误处理
    4. 明确的返回格式
    """
    
    name = "example_tool"
    description = """
    A well-documented tool that does X, Y, and Z.
    Use this tool when you need to: 
    - Perform action X
    - Get information about Y
    - Process data Z
    """
    parameters = [
        ToolParameter(
            name="required_param",
            type="string",
            description="A required parameter that specifies.. .",
            required=True
        ),
        ToolParameter(
            name="optional_param",
            type="integer",
            description="An optional parameter for...",
            required=False,
            default=10
        )
    ]
    
    def execute(self, required_param: str, optional_param: int = 10) -> str:
        """执行工具"""
        try:
            # 1. 参数验证
            if not required_param:
                return "Error: required_param cannot be empty"
            
            if optional_param < 0:
                return "Error: optional_param must be non-negative"
            
            # 2. 执行逻辑
            result = self._process(required_param, optional_param)
            
            # 3. 格式化返回
            return f"Success: {result}"
            
        except ValueError as e:
            return f"Validation Error: {str(e)}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"
    
    def _process(self, param1: str, param2: int) -> str:
        """内部处理逻辑"""
        # 实际的业务逻辑
        return f"Processed {param1} with {param2}"
```

### 7.4 实用工具示例

#### HTTP 请求工具

```python
import requests
from agent_coded_by_llm import BaseTool, ToolParameter

class HttpTool(BaseTool):
    """HTTP 请求工具"""
    
    name = "http_request"
    description = "Make HTTP requests to external APIs"
    parameters = [
        ToolParameter("url", "string", "The URL to request"),
        ToolParameter("method", "string", "HTTP method (GET/POST)", required=False, default="GET")
    ]
    
    def execute(self, url: str, method: str = "GET") -> str:
        try:
            if method. upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST": 
                response = requests. post(url, timeout=10)
            else:
                return f"Error: Unsupported method {method}"
            
            return f"Status: {response.status_code}, Body: {response.text[: 500]}"
        except requests.RequestException as e: 
            return f"Request Error: {str(e)}"
```

#### 文件读取工具

```python
import os
from agent_coded_by_llm import BaseTool, ToolParameter

class FileReaderTool(BaseTool):
    """文件读取工具"""
    
    name = "read_file"
    description = "Read contents of a local file"
    parameters = [
        ToolParameter("filepath", "string", "Path to the file to read")
    ]
    
    def __init__(self, allowed_dirs: list = None):
        """
        Args:
            allowed_dirs: 允许访问的目录列表（安全限制）
        """
        self.allowed_dirs = allowed_dirs or [os.getcwd()]
    
    def execute(self, filepath: str) -> str:
        # 安全检查
        abs_path = os. path.abspath(filepath)
        if not any(abs_path.startswith(d) for d in self.allowed_dirs):
            return "Error: Access denied - path not in allowed directories"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File content ({len(content)} chars):\n{content[: 1000]}"
        except FileNotFoundError: 
            return f"Error: File not found:  {filepath}"
        except Exception as e: 
            return f"Error reading file: {str(e)}"
```

---

## 8. 高级配置

### 8.1 自定义 Prompt

修改 `agent/prompt.py` 文件自定义系统提示词：

```python
# agent/prompt.py

REACT_SYSTEM_PROMPT = """你是一个专业的{domain}助手... 

## 可用工具: 
{tools}

## 响应格式: 
... 
"""
```

### 8.2 多 Agent 协作

```python
# 创建专门的工具注册器
math_registry = ToolRegistry()
math_registry.register(CalculatorTool())

search_registry = ToolRegistry()
search_registry.register(WikipediaSearchTool())

# 创建专门的 Agent
math_agent = ReActAgent(llm=llm, tool_registry=math_registry)
search_agent = ReActAgent(llm=llm, tool_registry=search_registry)

# 根据任务选择 Agent
def route_to_agent(query: str):
    if "计算" in query or "数学" in query: 
        return math_agent
    else:
        return search_agent
```

### 8.3 自定义解析器

```python
from agent_coded_by_llm. utils.parser import OutputParser

class CustomParser(OutputParser):
    """自定义输出解析器"""
    
    # 修改正则表达式以支持不同格式
    THOUGHT_PATTERN = r"思考:\s*(.*?)(?=行动:|$)"
    ACTION_PATTERN = r"行动:\s*(.*?)(?=行动输入:|$)"
    ACTION_INPUT_PATTERN = r"行动输入:\s*(.*?)$"
```

### 8.4 添加日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging. DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('agent_coded_by_llm')
```

### 8.5 错误重试机制

```python
from agent_coded_by_llm import ReActAgent
import time

class RetryAgent(ReActAgent):
    """带重试机制的 Agent"""
    
    def __init__(self, *args, max_retries:  int = 3, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_retries = max_retries
    
    def run(self, user_input: str):
        for attempt in range(self.max_retries):
            try:
                return super().run(user_input)
            except Exception as e: 
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                raise
```

---

## 9. API 参考

### 9.1 核心类

#### `LLMConfig`

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `api_key` | `str` | - | API 密钥（必填） |
| `base_url` | `str` | `https://api.deepseek.com` | API 基础 URL |
| `model` | `str` | `deepseek-chat` | 模型名称 |
| `temperature` | `float` | `0.7` | 生成温度 |
| `max_tokens` | `int` | `4096` | 最大输出长度 |

#### `AgentConfig`

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `max_iterations` | `int` | `10` | 最大迭代次数 |
| `verbose` | `bool` | `True` | 是否输出详细日志 |
| `stream` | `bool` | `True` | 是否使用流式输出 |

#### `ToolParameter`

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `name` | `str` | - | 参数名称 |
| `type` | `str` | - | 参数类型 |
| `description` | `str` | - | 参数描述 |
| `required` | `bool` | `True` | 是否必填 |
| `default` | `Any` | `None` | 默认值 |

### 9.2 主要方法

#### `BaseLLM.chat()`

```python
def chat(
    messages: List[Dict[str, str]],
    stream: bool = False,
    **kwargs
) -> LLMResponse | Generator[str, None, None]
```

#### `ReActAgent.run()`

```python
def run(user_input: str) -> AgentResult
```

#### `ReActAgent.run_stream()`

```python
def run_stream(user_input: str) -> Generator[Dict[str, Any], None, AgentResult]
```

输出类型：

| type | 描述 |
|------|------|
| `status` | 状态信息 |
| `thinking` | 开始思考 |
| `stream` | 流式内容片段 |
| `tool_call` | 调用工具 |
| `observation` | 工具返回结果 |
| `answer` | 最终答案 |
| `error` | 错误信息 |

#### `ToolRegistry.register()`

```python
def register(tool: BaseTool) -> None
```

#### `ToolRegistry.execute()`

```python
def execute(tool_name: str, **kwargs) -> str
```

---

## 10. 常见问题

### Q1: API 调用失败，提示 "Invalid API Key"

**解决方案**：
1. 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确
2. 确认 API Key 是否已激活
3. 检查账户余额是否充足

### Q2: Agent 陷入无限循环

**解决方案**：
1. 调整 `max_iterations` 参数
2. 优化 Prompt，使 Agent 更容易判断何时结束
3. 检查工具返回是否提供了足够的信息

### Q3: 工具执行结果未被正确使用

**解决方案**：
1. 确保工具返回格式清晰、易于理解
2. 在工具描述中明确说明返回格式
3. 检查 Observation 是否正确传递给 LLM

### Q4: 流式输出显示异常

**解决方案**：
1. 确保终端支持 UTF-8 编码
2. 使用 `flush=True` 确保实时输出
3. 检查网络连接稳定性

### Q5: 如何支持其他 LLM？

```python
# 修改 LLMConfig 即可支持任何 OpenAI 兼容的 API
config = LLMConfig(
    api_key="your-key",
    base_url="https://api.openai.com/v1",  # OpenAI
    # base_url="https://api.anthropic. com/v1",  # Claude (需要适配)
    model="gpt-4"
)
```

### Q6: 如何添加对话历史记忆？

```python
class MemoryAgent(ReActAgent):
    """带记忆的 Agent"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_history = []
    
    def run(self, user_input: str):
        # 将历史添加到消息中
        self.messages.extend(self.conversation_history)
        
        result = super().run(user_input)
        
        # 保存本轮对话
        self.conversation_history.append(
            {"role": "user", "content":  user_input}
        )
        self.conversation_history. append(
            {"role": "assistant", "content": result. final_answer}
        )
        
        return result
```

---

## 11. 最佳实践

### 11.1 工具设计原则

1. **单一职责**：每个工具只做一件事
2. **清晰描述**：让 LLM 能准确理解何时使用
3. **健壮处理**：优雅处理各种错误情况
4. **明确返回**：返回结构化、易于理解的结果

### 11.2 Prompt 优化

1. **提供示例**：在系统 Prompt 中包含使用示例
2. **明确格式**：强调输出格式要求
3. **设置边界**：说明工具的限制和适用场景

### 11.3 性能优化

1. **合理设置 max_iterations**：避免不必要的循环
2. **使用流式输出**：提升用户体验
3. **工具缓存**：对于重复查询，考虑缓存结果

### 11.4 安全建议

1. **参数验证**：在工具中验证所有输入
2. **权限控制**：限制工具的访问范围
3. **日志记录**：记录所有工具调用
4. **错误隔离**：工具错误不应影响整体运行

---

## 附录 A: 完整示例代码

```python
"""完整的 ReAct Agent 使用示例"""

import os
from dotenv import load_dotenv
from agent_coded_by_llm import (
    BaseLLM, LLMConfig, ReActAgent, AgentConfig,
    BaseTool, ToolParameter, tool,
    ToolRegistry, register_builtin_tools
)

# 加载环境变量
load_dotenv()

# ============ 自定义工具 ============

class StockPriceTool(BaseTool):
    """股票价格查询工具"""
    name = "stock_price"
    description = "Get current stock price for a given symbol"
    parameters = [
        ToolParameter("symbol", "string", "Stock symbol like AAPL, GOOGL")
    ]
    
    def execute(self, symbol: str) -> str:
        # 模拟数据
        prices = {"AAPL":  175.50, "GOOGL": 140.25, "MSFT":  378.90}
        if symbol. upper() in prices:
            return f"{symbol. upper()}: ${prices[symbol.upper()]}"
        return f"Error: Unknown symbol {symbol}"


@tool(
    name="currency_convert",
    description="Convert between currencies",
    parameters=[
        ToolParameter("amount", "number", "Amount to convert"),
        ToolParameter("from_currency", "string", "Source currency code"),
        ToolParameter("to_currency", "string", "Target currency code")
    ]
)
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    rates = {"USD": 1, "EUR": 0.85, "CNY": 7.24, "JPY": 149.50}
    from_rate = rates. get(from_currency.upper())
    to_rate = rates.get(to_currency.upper())
    
    if from_rate and to_rate: 
        result = amount * (to_rate / from_rate)
        return f"{amount} {from_currency} = {result:. 2f} {to_currency}"
    return "Error: Unknown currency"


def main():
    # 配置 LLM
    llm = BaseLLM(LLMConfig(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat",
        temperature=0.5
    ))
    
    # 创建工具注册器
    registry = ToolRegistry()
    register_builtin_tools(registry)
    registry.register(StockPriceTool())
    registry.register(currency_converter)
    
    # 创建 Agent
    agent = ReActAgent(
        llm=llm,
        tool_registry=registry,
        config=AgentConfig(max_iterations=8, stream=True)
    )
    
    # 测试查询
    queries = [
        "现在几点了？",
        "计算 (100 + 50) * 2",
        "AAPL 的股价是多少？",
        "把 100 美元换成人民币是多少？"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"📝 Query: {query}")
        print('='*60)
        
        for output in agent.run_stream(query):
            if output["type"] == "stream":
                print(output["content"], end="", flush=True)
            elif output["type"] in ["answer", "error"]:
                print(output["content"])


if __name__ == "__main__": 
    main()
```

---

**文档版本**:  v0.0.1  
**最后更新**: 2026-01-07  
**作者**: LLM