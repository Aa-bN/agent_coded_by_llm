"""
输出解析器模块
负责解析 LLM 的输出，提取 Thought、Action 和 Action Input
"""

import re
import json
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """动作类型枚举"""
    TOOL = "tool"  # 调用工具
    FINISH = "finish"  # 结束对话
    INVALID = "invalid"  # 无效动作


@dataclass
class ParsedResponse:
    """解析后的响应"""
    thought: str
    action: str
    action_input: Any
    action_type: ActionType
    raw_content: str

    @property
    def is_finished(self) -> bool:
        """是否已完成"""
        return self.action_type == ActionType.FINISH


class OutputParser:
    """
    LLM 输出解析器
    从 ReAct 格式的输出中提取结构化信息
    """

    # 正则表达式模式
    THOUGHT_PATTERN = r"Thought:\s*(.*?)(?=Action:|$)"
    ACTION_PATTERN = r"Action:\s*(.*?)(?=Action Input:|$)"
    ACTION_INPUT_PATTERN = r"Action Input:\s*(.*?)$"

    def parse(self, content: str) -> ParsedResponse:
        """
        解析 LLM 输出

        Args:
            content: LLM 的原始输出

        Returns:
            ParsedResponse 对象
        """
        # 提取 Thought
        thought = self._extract_thought(content)

        # 提取 Action
        action = self._extract_action(content)

        # 提取 Action Input
        action_input = self._extract_action_input(content)

        # 确定动作类型
        action_type = self._determine_action_type(action)

        # 如果是工具调用，尝试解析 JSON
        if action_type == ActionType.TOOL:
            action_input = self._parse_json_input(action_input)

        return ParsedResponse(
            thought=thought,
            action=action,
            action_input=action_input,
            action_type=action_type,
            raw_content=content
        )

    def _extract_thought(self, content: str) -> str:
        """提取 Thought 部分"""
        match = re.search(self.THOUGHT_PATTERN, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_action(self, content: str) -> str:
        """提取 Action 部分"""
        match = re.search(self.ACTION_PATTERN, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
        return ""

    def _extract_action_input(self, content: str) -> str:
        """提取 Action Input 部分"""
        match = re.search(self.ACTION_INPUT_PATTERN, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _determine_action_type(self, action: str) -> ActionType:
        """确定动作类型"""
        if not action:
            return ActionType.INVALID
        if action == "finish":
            return ActionType.FINISH
        return ActionType.TOOL

    def _parse_json_input(self, input_str: str) -> Dict[str, Any]:
        """尝试将 Action Input 解析为 JSON"""
        if not input_str:
            return {}

        try:
            # 尝试直接解析
            return json.loads(input_str)
        except json.JSONDecodeError:
            # 尝试提取 JSON 部分
            json_match = re.search(r'\{.*\}', input_str, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # 如果都失败，返回原始字符串作为单一参数
            return {"input": input_str}


class StreamingParser:
    """
    流式输出解析器
    用于在流式输出过程中实时解析内容
    """

    def __init__(self):
        self.buffer = ""
        self.thought_complete = False
        self.action_complete = False

    def feed(self, chunk: str) -> Optional[Dict[str, str]]:
        """
        向解析器输入新的内容片段

        Args:
            chunk: 新的内容片段

        Returns:
            如果检测到完整的部分，返回该部分的信息
        """
        self.buffer += chunk

        # 检查是否有完整的 Thought
        if not self.thought_complete and "Action:" in self.buffer:
            self.thought_complete = True
            thought_match = re.search(r"Thought:\s*(.*?)(?=Action: )", self.buffer, re.DOTALL)
            if thought_match:
                return {"type": "thought", "content": thought_match.group(1).strip()}

        # 检查是否有完整的 Action
        if self.thought_complete and not self.action_complete and "Action Input:" in self.buffer:
            self.action_complete = True
            action_match = re.search(r"Action:\s*(.*?)(?=Action Input:)", self.buffer, re.DOTALL)
            if action_match:
                return {"type": "action", "content": action_match.group(1).strip()}

        return None

    def reset(self):
        """重置解析器状态"""
        self.buffer = ""
        self.thought_complete = False
        self.action_complete = False