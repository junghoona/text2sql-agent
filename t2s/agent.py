"""The agent loop: Claude writes SQL, we run it, Claude reads results, repeat."""
import json

import anthropic
from dotenv import load_dotenv

from t2s import db

load_dotenv()
MODEL = "claude-opus-5-5"
SYSTEM = """You answer questions about a SQLite database by calling run_sql.
Inspect results, fix errors and retry if needed, then answer concisely.
Show the final SQL you used. Schema:

{schema}"""
TOOLS = [{
    "name": "run_sql",
    "description": "Run one read-only SQLite SELECT query. Returns columns and up to 200 rows.",
    "input_schema": {"type": "object", "required": ["sql"], "additionalProperties": False,
                     "properties": {"sql": {"type": "string", "description": "One SELECT statement."}}},
    "strict": True,
}]
client = anthropic.Anthropic()


def run_tool(sql: str) -> tuple[str, bool]:
    """Execute the query; errors go back to Claude so it can self-correct."""
    try:
        return json.dumps(db.run_query(sql), default=str), False
    except Exception as e:  # noqa: BLE001 - surface any DB error to the model
        return f"Error: {e}", True


def ask(messages: list, max_steps: int = 8) -> str:
    """Run the loop on `messages` (mutated in place) and return Claude's final text."""
    system = SYSTEM.format(schema=db.get_schema())
    for _ in range(max_steps):
        resp = client.beta.messages.create(
            model=MODEL, max_tokens=16000, system=system, tools=TOOLS, messages=messages,
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text") or f"[{resp.stop_reason}]"
        results = []
        for block in (b for b in resp.content if b.type == "tool_use"):
            out, is_err = run_tool(block.input["sql"])
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": out, "is_error": is_err})
        messages.append({"role": "user", "content": results})
    return "Stopped: too many steps."
