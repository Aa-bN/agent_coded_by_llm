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
    支持多语言回退搜索，提升搜索成功率
    """

    name = "wikipedia"
    description = "在维基百科上搜索信息，返回主题的简要摘要。支持中英文搜索。"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="要查询的搜索词或主题"
        )
    ]

    # 按优先级排列的语言列表
    LANGUAGE_FALLBACK = ['zh', 'en']

    def __init__(self):
        self._wiki_cache = {}

    def _get_wiki(self, language:  str) -> wikipediaapi.Wikipedia:
        """获取指定语言的 Wikipedia 实例（带缓存）"""
        if language not in self._wiki_cache:
            self._wiki_cache[language] = wikipediaapi.Wikipedia(
                user_agent='MyAgent/1.0 (https://github.com/Aa-bN/my-agent; your-email@gmail. com)',
                language=language
            )
        return self._wiki_cache[language]

    def _search_in_language(self, query: str, language: str) -> wikipediaapi.WikipediaPage | None:
        """在指定语言中搜索，返回页面或 None"""
        wiki = self._get_wiki(language)
        page = wiki.page(query)
        return page if page.exists() else None

    def _get_chinese_version(self, page: wikipediaapi. WikipediaPage) -> wikipediaapi.WikipediaPage | None:
        """尝试获取页面的中文版本"""
        langlinks = page.langlinks
        if 'zh' in langlinks:
            zh_wiki = self._get_wiki('zh')
            zh_page = zh_wiki.page(langlinks['zh']. title)
            if zh_page.exists():
                return zh_page
        return None

    def execute(self, query:  str) -> str:
        """执行 Wikipedia 搜索并返回摘要"""
        try:
            found_page = None
            source_lang = None

            # 1. 按语言优先级尝试搜索
            for lang in self.LANGUAGE_FALLBACK:
                page = self._search_in_language(query, lang)
                if page:
                    found_page = page
                    source_lang = lang
                    break

            # 2. 如果没找到，返回失败信息
            if not found_page:
                return f"未找到关于 '{query}' 的维基百科文章。请尝试其他搜索词。"

            # 3. 如果在英文维基找到，尝试获取中文版本
            if source_lang == 'en':
                zh_page = self._get_chinese_version(found_page)
                if zh_page:
                    found_page = zh_page
                    source_lang = 'zh'

            # 4. 构建返回结果
            summary = found_page.summary
            if len(summary) > 500:
                summary = summary[: 500] + "..."

            # 如果最终结果是英文，添加提示
            lang_note = ""
            if source_lang == 'en':
                lang_note = "\n\n⚠️ 注意：该内容来自英文维基百科，暂无中文版本。"

            return f"**{found_page. title}**\n\n{summary}\n\n来源: {found_page.fullurl}{lang_note}"

        except Exception as e:
            return f"搜索维基百科时出错: {str(e)}"


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
