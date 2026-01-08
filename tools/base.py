"""
Tool 模块 - 工具基类和工具注册器
提供便捷的工具定义和注册机制
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
import functools


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)

    def to_prompt_string(self) -> str:
        """生成用于 Prompt 的工具描述"""
        params_str = ""
        if self.parameters:
            params_list = []
            for p in self.parameters:
                req_str = "required" if p.required else "optional"
                params_list.append(f"    - {p.name} ({p.type}, {req_str}): {p.description}")
            params_str = "\n" + "\n".join(params_list)

        return f"- {self.name}:  {self.description}{params_str}"


class BaseTool(ABC):
    """
    工具基类
    所有自定义工具都应继承此类
    """

    # 子类需要定义这些属性
    name: str = ""
    description: str = ""
    parameters: List[ToolParameter] = []

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        执行工具

        Args:
            **kwargs:  工具参数

        Returns:
            工具执行结果的字符串表示
        """
        pass

    def get_definition(self) -> ToolDefinition:
        """获取工具定义"""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )

    def __call__(self, **kwargs) -> str:
        """使工具可直接调用"""
        return self.execute(**kwargs)


class ToolRegistry:
    """
    工具注册器
    管理所有可用工具的注册和获取
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        注册一个工具实例

        Args:
            tool: 工具实例
        """
        if not tool.name:
            raise ValueError("Tool must have a name")
        self._tools[tool.name] = tool

    def register_class(self, tool_class: type) -> type:
        """
        注册一个工具类（作为类装饰器使用）

        Args:
            tool_class: 工具类

        Returns:
            原工具类
        """
        tool_instance = tool_class()
        self.register(tool_instance)
        return tool_class

    def get(self, name: str) -> Optional[BaseTool]:
        """获取指定名称的工具"""
        return self._tools.get(name)

    def get_all(self) -> Dict[str, BaseTool]:
        """获取所有注册的工具"""
        return self._tools.copy()

    def get_tools_prompt(self) -> str:
        """生成所有工具的 Prompt 描述"""
        if not self._tools:
            return "No tools available."

        tool_descriptions = []
        for tool in self._tools.values():
            tool_descriptions.append(tool.get_definition().to_prompt_string())

        return "\n".join(tool_descriptions)

    def execute(self, tool_name: str, **kwargs) -> str:
        """
        执行指定工具

        Args:
            tool_name: 工具名称
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        tool = self.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"

        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}':  {str(e)}"


class FunctionTool(BaseTool):
    """
    函数工具类
    将普通函数包装为工具，用于 @tool 装饰器
    """

    def __init__(
            self,
            func: Callable,
            name: str,
            description: str,
            parameters: Optional[List[ToolParameter]] = None
    ):
        """
        初始化函数工具

        Args:
            func: 要包装的函数
            name: 工具名称
            description: 工具描述
            parameters: 参数列表
        """
        self._func = func
        self.name = name
        self.description = description
        self.parameters = parameters or []

    def execute(self, **kwargs) -> str:
        """执行包装的函数"""
        return self._func(**kwargs)


def tool(
        name: str,
        description: str,
        parameters: Optional[List[ToolParameter]] = None
) -> Callable:
    """
    工具装饰器 - 将普通函数转换为工具

    使用示例:
        @tool(
            name="calculator",
            description="A simple calculator",
            parameters=[
                ToolParameter("expression", "string", "Math expression to evaluate")
            ]
        )
        def calculator(expression: str) -> str:
            return str(eval(expression))

    Args:
        name: 工具名称
        description: 工具描述
        parameters:  参数列表

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> FunctionTool:
        # 保留原函数的元信息
        @functools.wraps(func)
        def wrapper(**kwargs) -> str:
            return func(**kwargs)

        # 创建并返回 FunctionTool 实例
        return FunctionTool(
            func=wrapper,
            name=name,
            description=description,
            parameters=parameters
        )

    return decorator


# 全局工具注册器实例
default_registry = ToolRegistry()
