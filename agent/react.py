"""
ReAct Agent 核心模块
实现 ReAct (Reasoning + Acting) 模式的 Agent
"""

from typing import Generator, List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

from ..llm.base import BaseLLM, LLMConfig
from ..tools.base import ToolRegistry, default_registry
from ..utils.parser import OutputParser, ParsedResponse, ActionType, StreamingParser
from .prompt import (
    REACT_SYSTEM_PROMPT,
    USER_MESSAGE_TEMPLATE,
    TOOL_RESULT_TEMPLATE,
    ERROR_TEMPLATE
)


@dataclass
class AgentConfig:
    """Agent 配置"""
    max_iterations: int = 10  # 最大迭代次数，防止无限循环
    verbose: bool = True  # 是否输出详细日志
    stream: bool = True  # 是否使用流式输出


@dataclass
class AgentStep:
    """Agent 执行步骤记录"""
    step_number: int
    thought: str
    action: str
    action_input: Any
    observation: str = ""
    is_final: bool = False


@dataclass
class AgentResult:
    """Agent 执行结果"""
    success: bool
    final_answer: str
    steps: List[AgentStep] = field(default_factory=list)
    error: Optional[str] = None
    total_iterations: int = 0


class ReActAgent:
    """
    ReAct Agent 实现
    采用 Thought -> Action -> Observation 循环模式
    """

    def __init__(
            self,
            llm: BaseLLM,
            tool_registry: Optional[ToolRegistry] = None,
            config: Optional[AgentConfig] = None
    ):
        """
        初始化 ReAct Agent

        Args:
            llm: LLM 实例
            tool_registry: 工具注册器，默认使用全局注册器
            config: Agent 配置
        """
        self.llm = llm
        self.tools = tool_registry or default_registry
        self.config = config or AgentConfig()
        self.parser = OutputParser()

        # 对话历史
        self.messages: List[Dict[str, str]] = []

        # 执行步骤记录
        self.steps: List[AgentStep] = []

    def _build_system_prompt(self) -> str:
        """构建系统 Prompt"""
        tools_description = self.tools.get_tools_prompt()
        return REACT_SYSTEM_PROMPT.format(tools=tools_description)

    def _log(self, message: str, level: str = "INFO"):
        """日志输出"""
        if self.config.verbose:
            print(f"[{level}] {message}")

    def reset(self):
        """重置 Agent 状态"""
        self.messages = []
        self.steps = []

    def run(self, user_input: str) -> AgentResult:
        """
        运行 Agent（非流式模式）

        Args:
            user_input: 用户输入

        Returns:
            AgentResult 对象
        """
        self.reset()

        # 初始化消息
        self.messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": USER_MESSAGE_TEMPLATE.format(user_input=user_input)}
        ]

        iteration = 0

        while iteration < self.config.max_iterations:
            iteration += 1
            self._log(f"=== Iteration {iteration} ===")

            # 调用 LLM
            try:
                response = self.llm.chat(self.messages, stream=False)
                content = response.content
                self._log(f"LLM Response:\n{content}")
            except Exception as e:
                return AgentResult(
                    success=False,
                    final_answer="",
                    steps=self.steps,
                    error=f"LLM call failed: {str(e)}",
                    total_iterations=iteration
                )

            # 解析响应
            parsed = self.parser.parse(content)

            # 记录步骤
            step = AgentStep(
                step_number=iteration,
                thought=parsed.thought,
                action=parsed.action,
                action_input=parsed.action_input
            )

            # 检查是否完成
            if parsed.is_finished:
                step.is_final = True
                step.observation = "Task completed"
                self.steps.append(step)

                return AgentResult(
                    success=True,
                    final_answer=str(parsed.action_input),
                    steps=self.steps,
                    total_iterations=iteration
                )

            # 执行工具
            if parsed.action_type == ActionType.TOOL:
                observation = self._execute_tool(parsed.action, parsed.action_input)
                step.observation = observation
                self._log(f"Tool Result: {observation}")

                # 将工具结果添加到消息中
                self.messages.append({"role": "assistant", "content": content})
                self.messages.append({
                    "role": "user",
                    "content": TOOL_RESULT_TEMPLATE.format(result=observation)
                })
            else:
                # 无效动作
                step.observation = "Invalid action format"
                self.messages.append({"role": "assistant", "content": content})
                self.messages.append({
                    "role": "user",
                    "content": ERROR_TEMPLATE.format(error="Invalid action format.  Please follow the correct format.")
                })

            self.steps.append(step)

        # 达到最大迭代次数
        return AgentResult(
            success=False,
            final_answer="",
            steps=self.steps,
            error=f"Max iterations ({self.config.max_iterations}) reached",
            total_iterations=iteration
        )

    def run_stream(self, user_input: str) -> Generator[Dict[str, Any], None, AgentResult]:
        """
        运行 Agent（流式模式）

        Args:
            user_input: 用户输入

        Yields:
            实时输出的内容片段，格式为 {"type": ".. .", "content": "..."}
            type 可以是:  "thought", "action", "observation", "answer", "error"

        Returns:
            AgentResult 对象
        """
        self.reset()

        # 初始化消息
        self.messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": USER_MESSAGE_TEMPLATE.format(user_input=user_input)}
        ]

        iteration = 0

        while iteration < self.config.max_iterations:
            iteration += 1
            yield {"type": "status", "content": f"\n=== Step {iteration} ===\n"}

            # 流式调用 LLM
            try:
                full_content = ""
                stream_parser = StreamingParser()

                yield {"type": "thinking", "content": "Thinking:  "}

                for chunk in self.llm.chat(self.messages, stream=True):
                    full_content += chunk
                    yield {"type": "stream", "content": chunk}

                    # 实时解析
                    parsed_part = stream_parser.feed(chunk)
                    if parsed_part:
                        yield {"type": parsed_part["type"] + "_complete", "content": parsed_part["content"]}

                yield {"type": "stream", "content": "\n"}

            except Exception as e:
                yield {"type": "error", "content": f"LLM call failed:  {str(e)}"}
                return AgentResult(
                    success=False,
                    final_answer="",
                    steps=self.steps,
                    error=str(e),
                    total_iterations=iteration
                )

            # 解析完整响应
            parsed = self.parser.parse(full_content)

            # 记录步骤
            step = AgentStep(
                step_number=iteration,
                thought=parsed.thought,
                action=parsed.action,
                action_input=parsed.action_input
            )

            # 检查是否完成
            if parsed.is_finished:
                step.is_final = True
                step.observation = "Task completed"
                self.steps.append(step)

                yield {"type": "answer", "content": f"\n📝 Final Answer: {parsed.action_input}"}

                return AgentResult(
                    success=True,
                    final_answer=str(parsed.action_input),
                    steps=self.steps,
                    total_iterations=iteration
                )

            # 执行工具
            if parsed.action_type == ActionType.TOOL:
                yield {"type": "tool_call", "content": f"\n🔧 Calling tool: {parsed.action}"}

                observation = self._execute_tool(parsed.action, parsed.action_input)
                step.observation = observation

                yield {"type": "observation", "content": f"\n📊 Observation:  {observation}\n"}

                # 将工具结果添加到消息中
                self.messages.append({"role": "assistant", "content": full_content})
                self.messages.append({
                    "role": "user",
                    "content": TOOL_RESULT_TEMPLATE.format(result=observation)
                })
            else:
                step.observation = "Invalid action format"
                yield {"type": "error", "content": "\n⚠️ Invalid action format\n"}

                self.messages.append({"role": "assistant", "content": full_content})
                self.messages.append({
                    "role": "user",
                    "content": ERROR_TEMPLATE.format(error="Invalid action format")
                })

            self.steps.append(step)

        # 达到最大迭代次数
        yield {"type": "error", "content": f"\n❌ Max iterations ({self.config.max_iterations}) reached"}

        return AgentResult(
            success=False,
            final_answer="",
            steps=self.steps,
            error=f"Max iterations reached",
            total_iterations=iteration
        )

    def _execute_tool(self, tool_name: str, tool_input: Any) -> str:
        """
        执行工具

        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数

        Returns:
            工具执行结果
        """
        if isinstance(tool_input, dict):
            return self.tools.execute(tool_name, **tool_input)
        elif isinstance(tool_input, str):
            return self.tools.execute(tool_name, input=tool_input)
        else:
            return self.tools.execute(tool_name)
        