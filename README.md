# Text-to-SQL Chat Agent

Ask questions about a dataset in plain English. Claude writes SQL, runs it against SQLite,
reads the results (and fixes its own errors), then answers.

**Stack:** Python · Claude API · MCP · SQLite · Streamlit

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # then add your ANTHROPIC_API_KEY
# drop one or more Kaggle CSVs into data/raw/
python scripts/load_data.py       # builds data/app.db
python -m t2s.cli                 # terminal chat
streamlit run app.py              # or the web UI
pytest                            # safety-guard tests
```

## How it works

| File | Role |
|---|---|
| `scripts/load_data.py` | Every CSV in `data/raw/` becomes a table (loaded in chunks, so big files work) |
| `t2s/db.py` | Builds a schema summary for the prompt; runs queries **read-only** behind a SELECT-only guard |
| `t2s/agent.py` | The loop: Claude calls the `run_sql` tool, sees results or errors, retries, answers |
| `t2s/cli.py` / `app.py` | Chat front ends (terminal / Streamlit) |
| `t2s/mcp_server.py` | Stretch: expose `get_schema` + `run_sql` to any MCP client |

Safety has two layers: `check_sql` rejects anything that isn't a single `SELECT`/`WITH`,
and the connection opens with `mode=ro`, so SQLite refuses writes even if the guard misses one.

## Weekend checklist

- [ ] **Sat AM:** Pick a Kaggle dataset (aim for 500K+ rows), load it, look at the schema
- [ ] **Sat PM:** Get `python -m t2s.cli` answering 5 real questions
- [ ] Tune the system prompt in `agent.py` (add column meanings, example questions)
- [ ] **Sun AM:** Streamlit UI: show the SQL and results as a table, not just the answer
- [ ] Add tests for any new guard rules
- [ ] **Stretch:** Connect `mcp_server.py` to Claude Desktop / Claude Code
- [ ] Record a demo GIF and write the resume line:
      *"Built an NL-to-SQL agent that queries 500K+ rows via conversational interface"*
