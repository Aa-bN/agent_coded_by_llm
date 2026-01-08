"""
LLM 模块 - 封装大语言模型的调用逻辑
支持 OpenAI API 兼容的模型（如 DeepSeek）
"""

from typing import Generator, List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class LLMConfig:
    """LLM 配置类"""
    api_key: str
    base_url: str = "https://api.deepseek.com"  # DeepSeek API 地址
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4096


class LLMResponse:
    """LLM 响应封装类"""

    def __init__(self, content: str, usage: Optional[Dict] = None):
        self.content = content
        self.usage = usage or {}

    def __str__(self) -> str:
        return self.content


class BaseLLM:
    """
    LLM 基类
    封装与大语言模型的交互逻辑，支持普通调用和流式调用
    """

    def __init__(self, config: LLMConfig):
        """
        初始化 LLM

        Args:
            config: LLM 配置对象
        """
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def chat(
            self,
            messages: List[Dict[str, str]],
            stream: bool = False,
            **kwargs
    ) -> LLMResponse | Generator[str, None, None]:
        """
        发送聊天请求

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            stream: 是否使用流式输出
            **kwargs: 其他参数，会覆盖默认配置

        Returns:
            如果 stream=False，返回 LLMResponse
            如果 stream=True，返回生成器，逐步产出内容片段
        """
        # 合并默认参数和传入参数
        params = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": stream
        }

        if stream:
            return self._stream_chat(params)
        else:
            return self._sync_chat(params)

    def _sync_chat(self, params: Dict[str, Any]) -> LLMResponse:
        """同步调用 LLM"""
        response = self.client.chat.completions.create(**params)
        return LLMResponse(
            content=response.choices[0].message.content,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else {}
        )

    def _stream_chat(self, params: Dict[str, Any]) -> Generator[str, None, None]:
        """流式调用 LLM，逐步产出内容片段"""
        response = self.client.chat.completions.create(**params)
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                