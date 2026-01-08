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
