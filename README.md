# AI Time Comprehension

[![Tests](https://github.com/DLEXTRUCKER/Ai-time-Comprehension/actions/workflows/tests.yml/badge.svg)](https://github.com/DLEXTRUCKER/Ai-time-Comprehension/actions/workflows/tests.yml)

A lightweight temporal-context tool that helps large language models reason accurately about elapsed time without disrupting natural conversation.

## The problem

Conversational AI can access earlier messages but may not receive reliable timestamp information or accurately calculate elapsed time. This can cause errors such as describing something from minutes ago as though it happened yesterday.

## The solution

Every conversation message receives a trustworthy ISO 8601 timestamp. When elapsed time matters, GPT-5.6 calls a deterministic Python function with:

- The relevant earlier timestamp.
- The current message timestamp.

The function returns the exact elapsed time. GPT-5.6 then uses that result naturally without exposing technical metadata to the user.

## Example

```text
July 17 — User: I am going to do laundry and watch TV.

Two days pass.

July 19 — User: Remember when I said I was going to do laundry?
I forgot to put it in the dryer.
```

The model calculates that two days passed and can naturally recommend washing the damp laundry again.

## How it works

1. The application timestamps every message.
2. GPT-5.6 recognizes when elapsed time matters.
3. GPT-5.6 selects the relevant earlier timestamp.
4. It calls `calculate_elapsed_time`.
5. The Python function returns days, hours, minutes and seconds.
6. GPT-5.6 incorporates the result into its normal response.

## Project files

- `time_calculator.py` — deterministic timestamp calculation.
- `tool_adapter.py` — OpenAI function definition and dispatcher.
- `demo.py` — fixed GPT-5.6 demonstration conversation.
- `test_time_calculator.py` — calculator tests.
- `test_tool_adapter.py` — tool-adapter tests.
- `DECISIONS.md` — project decisions and ownership record.

## Running the tests

```bash
python -m unittest -v
```

The test suite covers:

- Minute and multi-day intervals.
- Crossing midnight.
- Different timezone offsets.
- Daylight-saving fallback.
- Missing timezone information.
- Reversed timestamps.
- Strict tool arguments.
- Tool dispatching.

## Running the GPT-5.6 demonstration

Requirements:

- Python 3.12 or newer.
- An OpenAI API key with available API credit.

Install the dependency:

```bash
python -m pip install -r requirements.txt
```

Set the API key as an environment variable. Do not place it in the repository.

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key-here"
python demo.py
```

Linux or macOS:

```bash
export OPENAI_API_KEY="your-key-here"
python demo.py
```

The demonstration reports whether GPT-5.6 called the elapsed-time tool before printing its natural response.

## Product decisions

James Lennox originated the problem and made the central design decisions:

- Keep the tool simple and deterministic.
- Let the LLM identify the relevant conversation message.
- Calculate elapsed time rather than replacing AI memory.
- Preserve natural conversational behaviour.
- Use direct OpenAI function calling to reduce complexity and cost.

See `DECISIONS.md` for the full decision record.

## Codex collaboration

Codex helped translate the product decisions into an implementation plan, generated the initial Python implementation, created automated tests, checked the code, and assisted with documentation.

The implementation was developed during OpenAI Build Week using Codex. The required Codex feedback session identifier will be added before submission.

## Current limitations

- The host application must provide trustworthy message timestamps.
- Timestamps must include a UTC offset or end in `Z`.
- The prototype assumes relevant conversation history is already available to the model.
- The included demonstration uses one fixed scenario.
- The tool calculates elapsed duration but leaves interpretation and wording to the LLM.

## Licence

Released under the MIT License.
