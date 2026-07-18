"""Minimal GPT-5.6 demonstration of temporal tool calling."""

from tool_adapter import ELAPSED_TIME_TOOL, execute_elapsed_time_tool


SYSTEM_INSTRUCTIONS = """
You are a natural conversational assistant. Every conversation message includes a
trusted ISO 8601 timestamp. Whenever elapsed time between messages could affect
your wording or reasoning, call calculate_elapsed_time with the relevant earlier
timestamp and the current message timestamp. Do not estimate elapsed time when
timestamps are available. Use the returned result naturally. Do not mention the
tool, timestamps, or calculation unless the user asks. Do not assume a planned
action was completed unless the conversation establishes that it happened.
""".strip()


DEMO_CONVERSATION = [
    {
        "role": "user",
        "content": (
            "[Timestamp: 2026-07-17T16:00:00-06:00] "
            "I am going to do laundry and watch a TV show."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "[Timestamp: 2026-07-17T16:00:05-06:00] "
            "Sounds good. Enjoy the show."
        ),
    },
    {
        "role": "user",
        "content": (
            "[Timestamp: 2026-07-19T16:05:00-06:00] "
            "Remember when I said I was going to do laundry? "
            "I forgot to put it in the dryer."
        ),
    },
]


def run_demo() -> None:
    """Run the fixed laundry scenario with GPT-5.6."""
    from openai import OpenAI

    client = OpenAI()
    input_items = list(DEMO_CONVERSATION)
    tool_was_used = False

    for _ in range(3):
        response = client.responses.create(
            model="gpt-5.6",
            reasoning={"effort": "low"},
            instructions=SYSTEM_INSTRUCTIONS,
            tools=[ELAPSED_TIME_TOOL],
            input=input_items,
            max_output_tokens=800,
        )
        calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not calls:
            print(f"Elapsed-time tool used: {tool_was_used}")
            print(response.output_text)
            return

        input_items += response.output

        for call in calls:
            if call.name != "calculate_elapsed_time":
                raise RuntimeError(
                    f"Unexpected tool call: {call.name}"
                )

            tool_was_used = True
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": execute_elapsed_time_tool(
                        call.arguments
                    ),
                }
            )

    raise RuntimeError(
        "GPT-5.6 did not finish after three tool-call rounds."
    )


if __name__ == "__main__":
    run_demo()
