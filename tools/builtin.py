"""
内置工具集
提供一些常用的内置工具
"""

import json
import datetime
from typing import Optional
from .base import BaseTool, ToolParameter, tool, default_registry

import wikipediaapi


class CalculatorTool(BaseTool):
    """计算器工具 - 执行数学表达式计算"""

    name = "calculator"
    description = "Evaluate mathematical expressions.  Supports basic arithmetic operations (+, -, *, /, **) and common math functions."
    parameters = [
        ToolParameter(
            name="expression",
            type="string",
            description="The mathematical expression to evaluate, e.g., '2 + 3 * 4' or '(10 + 5) / 3'"
        )
    ]

    def execute(self, expression: str) -> str:
        """执行数学表达式计算"""
        try:
            # 安全地计算表达式（仅允许数学运算）
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "pow": pow, "sum": sum, "len": len
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: Cannot evaluate expression '{expression}'.  Reason: {str(e)}"


class DateTimeTool(BaseTool):
    """日期时间工具 - 获取当前日期时间信息"""

    name = "datetime"
    description = "Get current date and time information."
    parameters = [
        ToolParameter(
            name="format",
            type="string",
            description="Output format:  'date' for date only, 'time' for time only, 'datetime' for both, 'timestamp' for Unix timestamp",
            required=False,
            default="datetime"
        )
    ]

    def execute(self, format: str = "datetime") -> str:
        """获取日期时间信息"""
        now = datetime.datetime.now()

        formats = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": str(int(now.timestamp()))
        }

        if format not in formats:
            return f"Error:  Unknown format '{format}'. Available formats: {list(formats.keys())}"

        return f"Current {format}: {formats[format]}"


class WikipediaSearchTool(BaseTool):
    """
    Wikipedia 搜索工具
    注意：这是一个模拟实现，实际使用时需要接入真实 API
    """

    name = "wikipedia_search"
    description = "Search for information on Wikipedia.  Returns a brief summary about the topic."
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="The search query or topic to look up"
        )
    ]

    def __init__(self):
        # 初始化 Wikipedia API，设置语言和 User-Agent
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='MyAgentBot/1.0 (https://example.com; contact@example.com)',
            language='en'  # en
        )

    def execute(self, query: str) -> str:

        # return f"[Wikipedia Mock] Searching for '{query}'...  In a real implementation, this would return Wikipedia content."
        """执行 Wikipedia 搜索并返回摘要"""
        try:
            # 获取页面
            page = self.wiki.page(query)

            # 检查页面是否存在
            if not page.exists():
                return f"未找到关于 '{query}' 的维基百科文章。请尝试其他搜索词。"

            # 返回摘要（前500字符以保持简洁）
            summary = page.summary
            if len(summary) > 500:
                summary = summary[: 500] + "..."

            return f"**{page.title}**\n\n{summary}\n\n来源: {page.fullurl}"

        except Exception as e:
            return f"搜索维基百科时出错: {str(e)}"


class WeatherTool(BaseTool):
    """
    天气查询工具
    注意：这是一个模拟实现，实际使用时需要接入真实天气 API
    """

    name = "weather"
    description = "Get current weather information for a specified city."
    parameters = [
        ToolParameter(
            name="city",
            type="string",
            description="The city name to get weather for"
        )
    ]

    def execute(self, city: str) -> str:
        """模拟天气查询"""
        # 模拟实现，实际应该调用天气 API
        return f"[Weather Mock] Weather in {city}:  Sunny, 25°C, Humidity: 60%.  (This is mock data)"


def register_builtin_tools(registry=None):
    """
    注册所有内置工具到指定注册器

    Args:
        registry: 工具注册器，默认使用全局注册器
    """
    if registry is None:
        registry = default_registry

    registry.register(CalculatorTool())
    registry.register(DateTimeTool())
    registry.register(WikipediaSearchTool())
    registry.register(WeatherTool())
