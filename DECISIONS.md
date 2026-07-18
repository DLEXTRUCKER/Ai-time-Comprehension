# Project Decision Log

## July 17, 2026 — Problem selected

**Decision maker:** James Lennox

Build a lightweight tool that gives conversational AI accurate elapsed-time information.

The project was inspired by AI systems incorrectly describing events from minutes ago as though they happened yesterday or during a much older conversation.

## July 17, 2026 — Scope simplified

**Decision maker:** James Lennox

The LLM already has access to the conversation and can determine which earlier message the user means. The project will not build a separate message-retrieval or memory system.

## July 17, 2026 — Core operation

**Decision maker:** James Lennox

Every message must have a trustworthy timestamp. When time matters, the LLM supplies the earlier timestamp and current timestamp to the tool. The tool returns the exact elapsed time.

## July 17, 2026 — Conversational behaviour

**Decision maker:** James Lennox

Temporal calculations must remain internal. The LLM should use the result naturally without sounding like a timestamp database or changing its existing conversational style.

## Codex collaboration

Codex helped translate these product decisions into a technical plan and will assist with implementation, testing, documentation, and demonstration preparation.
## July 17, 2026 — Integration method

**Decision maker:** James Lennox

Use direct OpenAI function calling instead of building a separate MCP server.

This keeps the prototype small, reduces dependencies and development time, minimizes API usage, and directly demonstrates GPT-5.6 deciding when to call the elapsed-time calculator.

## July 17, 2026 — Integration pivot

**Decision maker:** James Lennox

Pivot the primary integration from direct OpenAI Responses API calls to a local
Codex MCP server.

Build Week provides Codex access but no OpenAI API credits. A local stdio MCP
server lets Codex use the same deterministic elapsed-time calculator without
paid API calls. The earlier OpenAI dependency and prototype remain temporarily
for compatibility and reference; MCP is now the primary integration.

## July 18, 2026 — Timestamp gateway and trusted-local scope

**Decision maker:** James Lennox

James identified that the AI must not be responsible for ensuring messages
receive trustworthy timestamps. The project therefore added a host-controlled
gateway that automatically stamps user messages on receipt, stores canonical
append-only JSONL history, starts a fresh ephemeral Codex thread for each turn,
and stamps assistant messages only after successful completion.

The project explored a dedicated isolated `CODEX_HOME` architecture after
reviews identified inherited Codex app-server capabilities. Repeated targeted
reviews then exposed substantial credential, executable, environment, and
path-isolation complexity. James decided to remove that architecture and keep
the prototype intentionally simple: it uses the normally authenticated Codex
installation as a trusted-local Build Week demonstration, not as a hostile
multi-user security boundary.

The final gateway retains read-only sandboxing, restrictive approval settings,
approval-denial handlers, developer-instruction separation, and canonical
conversation history treated as untrusted data. James accepted the documented
v0.144.5 limitation that every built-in shell and file capability cannot be
removed per thread. For production, the preferred direction is a runtime or
app-server version with an explicit tool allowlist.

James made and approved the timestamp-authority, architecture, simplification,
and final scope decisions. Codex implemented, tested, debugged, and reviewed the
gateway. ChatGPT provided architecture guidance and recommended returning to the
simpler model after the isolation review findings.
