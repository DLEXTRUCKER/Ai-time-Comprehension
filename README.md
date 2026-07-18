# AI Time Comprehension

[![Tests](https://github.com/DLEXTRUCKER/Ai-time-Comprehension/actions/workflows/tests.yml/badge.svg)](https://github.com/DLEXTRUCKER/Ai-time-Comprehension/actions/workflows/tests.yml)

A small local MCP tool that gives conversational AI exact elapsed-time
calculations while preserving natural conversation. The live competition demo
uses `gpt-5.6-sol` through Codex and requires no OpenAI API key.

## The problem

Conversational AI can read earlier messages but may miscalculate how much time
has passed or use incorrect temporal wording. It can describe something from
minutes ago as if it happened yesterday, even when the conversation contains
enough context to answer accurately.

## The solution

Every message receives a trustworthy, timezone-aware ISO 8601 timestamp. When
elapsed time matters, GPT-5.6 selects the relevant earlier message and calls the
deterministic `calculate_elapsed_time` MCP tool with that timestamp and the
current timestamp.

The tool delegates to one deterministic calculator and returns:

```json
{
  "total_seconds": 173100,
  "days": 2,
  "hours": 0,
  "minutes": 5,
  "seconds": 0
}
```

GPT-5.6 then uses the result naturally instead of mechanically reciting
timestamps or metadata. Timestamps must include a UTC offset such as `-06:00`,
or end in `Z`.

## Example

```text
July 17 — User: I am going to do laundry and watch a TV show.

Two days pass.

July 19 — User: Remember when I said I was going to do laundry?
I forgot to put it in the dryer.
```

The model determines that two days have passed and can naturally recommend
rewashing the damp laundry before drying it. It does not need to expose the
tool call or recite timestamp metadata to the user.

## How it works

1. The host gives every conversation message a trustworthy timestamp.
2. GPT-5.6 identifies when elapsed time affects its reasoning or wording.
3. GPT-5.6 selects the relevant earlier message timestamp.
4. Codex calls the local `calculate_elapsed_time` MCP tool.
5. The deterministic calculator returns days, hours, minutes, and seconds.
6. GPT-5.6 incorporates the result into a natural response.

## Windows installation

Python 3.12 or newer is recommended. In PowerShell, from the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest -v
```

If PowerShell blocks activation, use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v
```

## Configure Codex

Add this stdio server to `%USERPROFILE%\.codex\config.toml`. Replace both paths
with absolute paths to your checkout:

```toml
[mcp_servers.ai_time_comprehension]
command = "C:\\path\\to\\Ai-time-Comprehension\\.venv\\Scripts\\python.exe"
args = ["C:\\path\\to\\Ai-time-Comprehension\\mcp_server.py"]
```

Restart Codex after saving the configuration. Codex launches this stdio server;
it does not need to run in a separate terminal.

## Demo

The live Build Week demo runs `gpt-5.6-sol` through Codex. Codex supplies access
to the model and launches the local MCP server, so no `OPENAI_API_KEY` or paid
API credit is required.

Start a new Codex conversation and ask:

```text
Use calculate_elapsed_time to find the elapsed time from
2026-07-17T16:00:00-06:00 to 2026-07-19T16:05:00-06:00.
```

Codex should call the local tool and report 2 days and 5 minutes.

For protocol-level inspection, the MCP SDK's optional CLI can run the server:

```powershell
.\.venv\Scripts\mcp.exe dev mcp_server.py
```

## Project files

- `time_calculator.py` — deterministic timestamp calculation.
- `mcp_server.py` — primary local Codex MCP integration.
- `test_mcp_server.py` — focused MCP wrapper tests.
- `test_time_calculator.py` — calculator and timestamp validation tests.
- `tool_adapter.py`, `test_tool_adapter.py`, and `demo.py` — previous Responses
  API prototype, retained temporarily for compatibility and reference.
- `DECISIONS.md` — product decision and ownership record.

## Running all tests

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

All 14 automated tests pass. The suite covers the calculator, timezone and
ordering validation, the retained OpenAI adapter, MCP tool registration,
structured results, and delegation to the deterministic calculator.

## Product decisions

James Lennox originated the problem and made the product and architecture
decisions:

- Keep the elapsed-time calculator deterministic.
- Let the model select the relevant earlier conversation message.
- Preserve natural conversational behavior instead of exposing tool metadata.
- Pivot from direct Responses API calls to Codex MCP after learning that Build
  Week provides Codex access but no OpenAI API credits.

The MCP wrapper deliberately contains no time logic.
`time_calculator.calculate_elapsed_time` remains the single source of truth.

## Codex collaboration

Codex helped implement the MCP server, write the automated tests and
documentation, run review, and catch the missing MCP CLI dependency required by
the documented `mcp dev` workflow. James made the product and architecture
decisions, including the scope, deterministic design, model responsibility, and
integration pivot.

## Current limitations

- The host must provide trustworthy timestamps for every message.
- Timestamps must include a UTC offset or end in `Z`.
- Relevant conversation history must already be available to the model.
- The model is responsible for selecting the correct earlier message.
- The tool calculates elapsed duration but leaves interpretation and wording to
  the model.
- The competition demo uses a fixed scenario rather than a complete chat host.
- The earlier Responses API prototype remains in the repository but is no
  longer the primary integration.

## Licence

Released under the MIT License.
