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

## Automatic timestamp gateway architecture

The interactive gateway makes the host, rather than the model, the timestamp
authority:

1. The host stamps each user message in UTC when it is received.
2. The message is appended to the canonical JSONL conversation log.
3. A fresh, ephemeral Codex thread receives the complete timestamped history as
   untrusted conversation data.
4. GPT-5.6 Sol selects the relevant earlier message and calls the deterministic
   `calculate_elapsed_time` MCP tool when elapsed time matters.
5. After a successful turn, the host stamps and appends the assistant response.
6. The model uses the exact result while preserving natural conversational
   wording.

The JSONL log is append-only and is the canonical source of conversation order.
Assistant output is not stored when a turn fails.

## Run the timestamped chat on Windows

From the project directory:

```powershell
.\.venv\Scripts\python.exe chat_gateway.py
```

Enter `/quit` or `/exit` to close the conversation cleanly. To inspect the CLI
without starting Codex app-server:

```powershell
.\.venv\Scripts\python.exe chat_gateway.py --help
```

## Live gateway validation

The live validation used Codex app-server with existing ChatGPT authentication;
no OpenAI API key was used. A natural multi-turn conversation succeeded, and
the model retrieved the correct earlier laundry and TV-show messages. It
reported 12 minutes 6 seconds from the first message, then 12 minutes 34 seconds
from the TV-show message. All 41 automated tests passed before this successful
live test.

## Gateway security exploration and scope decision

Reviews identified that Codex app-server v0.144.5 inherits built-in
capabilities. The project explored an isolated `CODEX_HOME` design, but repeated
targeted reviews exposed credential, executable, environment, and path-isolation
complexity. James removed that design because this is a trusted-local Build Week
prototype, not a hostile multi-user security boundary.

The simplified gateway retains read-only sandboxing, restrictive approval
settings, approval-denial handlers, developer-instruction separation, and a
canonical history supplied as untrusted conversation data. A current platform
limitation remains: app-server v0.144.5 cannot technically remove every built-in
shell or file capability per thread. A future production version should use a
runtime or app-server release that supports an explicit tool allowlist.

## Gateway project files

- `timestamp_gateway.py` provides automatic UTC timestamping and the append-only
  canonical JSONL log.
- `chat_gateway.py` provides the interactive Codex app-server conversation
  gateway.
- `test_timestamp_gateway.py` and `test_chat_gateway.py` cover timestamp,
  persistence, protocol, failure, and shutdown behavior.

Private live logs matching `conversation*.jsonl` remain local through
`.gitignore`.

## Gateway collaboration

James identified the timestamp-authority weakness and made the product,
architecture, and scope decisions. Codex implemented, tested, debugged, and
reviewed the code. ChatGPT provided architecture guidance and recommended
returning to the simpler model after the isolation findings. James approved the
final trusted-local direction.
