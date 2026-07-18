# AI Time Comprehension

[![Tests](https://github.com/DLEXTRUCKER/Ai-time-Comprehension/actions/workflows/tests.yml/badge.svg)](https://github.com/DLEXTRUCKER/Ai-time-Comprehension/actions/workflows/tests.yml)

A small local MCP tool that gives Codex exact elapsed-time calculations without
requiring paid API calls.

The server exposes `calculate_elapsed_time`. It accepts an earlier and current
timezone-aware ISO 8601 timestamp, delegates to the deterministic calculator,
and returns:

```json
{
  "total_seconds": 173100,
  "days": 2,
  "hours": 0,
  "minutes": 5,
  "seconds": 0
}
```

Timestamps must include a UTC offset (such as `-06:00`) or end in `Z`.

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

Start a new Codex conversation and ask:

```text
Use calculate_elapsed_time to find the elapsed time from
2026-07-17T16:00:00-06:00 to 2026-07-19T16:05:00-06:00.
```

Codex should call the local tool and report 2 days and 5 minutes. No
`OPENAI_API_KEY` is needed for this MCP demo.

For protocol-level inspection, the MCP SDK's optional CLI can run the server:

```powershell
.\.venv\Scripts\mcp.exe dev mcp_server.py
```

## Project files

- `time_calculator.py` — deterministic timestamp calculation.
- `mcp_server.py` — primary local Codex MCP integration.
- `test_mcp_server.py` — focused MCP wrapper tests.
- `tool_adapter.py` and `demo.py` — previous Responses API prototype, retained
  temporarily.
- `DECISIONS.md` — product decision and ownership record.

## Running all tests

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

The suite covers the calculator, timezone and ordering validation, the retained
OpenAI adapter, MCP tool registration, structured results, and delegation to
the deterministic calculator.

## Design

Codex selects the relevant timestamps. The MCP wrapper contains no time logic;
`time_calculator.calculate_elapsed_time` remains the single source of truth.
This keeps the behavior deterministic and the integration easy to understand.

The host must provide trustworthy timestamps and relevant conversation context.
Interpretation and conversational wording remain the model's responsibility.

## Licence

Released under the MIT License.
