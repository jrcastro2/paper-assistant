import json
from typing import Callable
import anthropic


def run_agent(user_question: str, tool_functions: dict[str, Callable], tools: list[dict]) -> str:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_question}]
    step = 0

    while True:
        step += 1
        print(f"\n--- step {step} ---")

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        print(f"stop_reason: {response.stop_reason}")

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if hasattr(b, "text"))

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"tool call: {block.name}({block.input})")
            result = tool_functions[block.name](**block.input)
            print(f"tool result: {result}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })

        messages.append({"role": "user", "content": tool_results})
