"""
ReAct Agent 主程序入口
演示如何使用 ReAct Agent
"""

import os
from dotenv import load_dotenv

from agent_coded_by_llm import (
    BaseLLM,
    LLMConfig,
    ReActAgent,
    AgentConfig,
    BaseTool,
    ToolParameter,
    tool,
    default_registry,
    register_builtin_tools
)


# ========== 自定义工具示例 ==========

# 方式1: 继承 BaseTool 类
class SearchEngineTool(BaseTool):
    """自定义搜索引擎工具"""

    name = "search"
    description = "Search the web for information.  Use this when you need to find current information or facts."
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="The search query"
        ),
        ToolParameter(
            name="num_results",
            type="integer",
            description="Number of results to return",
            required=False,
            default=5
        )
    ]

    def execute(self, query: str, num_results: int = 5) -> str:
        # 模拟搜索结果
        return f"[Search Mock] Top {num_results} results for '{query}':  ..."


# 方式2: 使用装饰器
@tool(
    name="translate",
    description="Translate text between languages",
    parameters=[
        ToolParameter("text", "string", "The text to translate"),
        ToolParameter("target_language", "string", "Target language code (e.g., 'en', 'zh', 'ja')")
    ]
)
def translate_tool(text: str, target_language: str) -> str:
    """翻译工具的模拟实现"""
    return f"[Translation Mock] '{text}' translated to {target_language}:  ..."


def setup_agent() -> ReActAgent:
    """
    设置并初始化 Agent

    Returns:
        配置好的 ReActAgent 实例
    """
    # 加载环境变量
    load_dotenv()

    # 配置 LLM（使用 DeepSeek）
    llm_config = LLMConfig(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=1.0
    )
    llm = BaseLLM(llm_config)

    # 注册内置工具
    register_builtin_tools(default_registry)

    # 注册自定义工具
    default_registry.register(SearchEngineTool())
    default_registry.register(translate_tool)  # 装饰器返回的是工具实例

    # 配置 Agent
    agent_config = AgentConfig(
        max_iterations=10,
        verbose=True,
        stream=True
    )

    # 创建 Agent
    agent = ReActAgent(
        llm=llm,
        tool_registry=default_registry,
        config=agent_config
    )

    return agent


def run_interactive_mode(agent: ReActAgent):
    """
    交互式对话模式

    Args:
        agent: ReActAgent 实例
    """
    print("=" * 60)
    print("🤖 ReAct Agent Interactive Mode")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'tools' to list available tools")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break

            if user_input.lower() == 'tools':
                print("\n📦 Available Tools:")
                print(agent.tools.get_tools_prompt())
                continue

            print("\n🤖 Agent:")

            # 使用流式模式运行
            if agent.config.stream:
                result = None
                for output in agent.run_stream(user_input):
                    if output["type"] == "stream":
                        print(output["content"], end="", flush=True)
                    elif output["type"] in ["tool_call", "observation", "answer", "error", "status"]:
                        print(output["content"])
                # 获取最终结果
                # result 在生成器结束时返回
            else:
                result = agent.run(user_input)
                print(f"\n📝 Final Answer: {result.final_answer}")

                if not result.success:
                    print(f"⚠️ Warning: {result.error}")

        except KeyboardInterrupt:
            print("\n👋 Interrupted.  Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error:  {str(e)}")


def run_single_query(agent: ReActAgent, query: str):
    """
    单次查询模式

    Args:
        agent: ReActAgent 实例
        query: 用户查询
    """
    print(f"📝 Query: {query}")
    print("-" * 40)

    if agent.config.stream:
        for output in agent.run_stream(query):
            if output["type"] == "stream":
                print(output["content"], end="", flush=True)
            elif output["type"] in ["tool_call", "observation", "answer", "error", "status"]:
                print(output["content"])
    else:
        result = agent.run(query)
        print(f"\n📝 Final Answer: {result.final_answer}")
        print(f"📊 Total Steps: {result.total_iterations}")

        if result.steps:
            print("\n📋 Execution Steps:")
            for step in result.steps:
                print(f"  Step {step.step_number}:")
                print(f"    Thought: {step.thought[: 100]}...")
                print(f"    Action: {step.action}")
                print(f"    Observation: {step.observation[:100]}...")


def main():
    """主函数"""
    # 初始化 Agent
    agent = setup_agent()

    # 显示可用工具
    print("\n📦 Registered Tools:")
    print(agent.tools.get_tools_prompt())
    print()

    # 选择运行模式
    import sys

    if len(sys.argv) > 1:
        # 命令行参数模式
        query = " ".join(sys.argv[1:])
        run_single_query(agent, query)
    else:
        # 交互式模式
        run_interactive_mode(agent)


if __name__ == "__main__":
    main()
