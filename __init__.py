"""
ReAct Agent Package
一个模块化的 ReAct 模式 Agent 实现
"""

from .llm.base import BaseLLM, LLMConfig, LLMResponse
from .tools.base import (
    BaseTool,
    ToolParameter,
    ToolDefinition,
    ToolRegistry,
    tool,
    default_registry
)
from .tools.builtin import register_builtin_tools
from .agent.react import ReActAgent, AgentConfig, AgentResult, AgentStep
from .utils.parser import OutputParser, ParsedResponse, ActionType

__version__ = "1.0.0"

__all__ = [
    # LLM
    "BaseLLM",
    "LLMConfig",
    "LLMResponse",

    # Tools
    "BaseTool",
    "ToolParameter",
    "ToolDefinition",
    "ToolRegistry",
    "tool",
    "default_registry",
    "register_builtin_tools",

    # Agent
    "ReActAgent",
    "AgentConfig",
    "AgentResult",
    "AgentStep",

    # Parser
    "OutputParser",
    "ParsedResponse",
    "ActionType",
]
