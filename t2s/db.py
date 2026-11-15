"""Schema introspection + guarded, read-only query execution."""
import os
import re
import sqlite3

DB_PATH = os.getenv("T2S_DB_PATH", "data/app.db")
MAX_ROWS = 200
WRITE_WORDS = "insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex"
FORBIDDEN = re.compile(rf"\b({WRITE_WORDS})\b", re.IGNORECASE)


def connect(path: str = DB_PATH) -> sqlite3.Connection:
    """Open the database in read-only mode (the real safety net)."""
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def get_schema(path: str = DB_PATH) -> str:
    """Return CREATE TABLE statements plus row counts, for the LLM's context."""
    with connect(path) as conn:
        q = "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        rows = conn.execute(q).fetchall()
        parts = []
        for name, sql in rows:
            count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            parts.append(f"-- {name}: {count} rows\n{sql};")
    return "\n\n".join(parts)


def check_sql(sql: str) -> None:
    """Raise ValueError unless sql is a single SELECT/WITH statement."""
    stmt = sql.strip().rstrip(";").strip()
    if not stmt:
        raise ValueError("Empty query.")
    if ";" in stmt:
        raise ValueError("Only one statement is allowed.")
    if not re.match(r"^(select|with)\b", stmt, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")
    if FORBIDDEN.search(stmt):
        raise ValueError("Query contains a forbidden keyword.")


def run_query(sql: str, path: str = DB_PATH) -> dict:
    """Validate, run, and return {'columns': [...], 'rows': [...]} (capped at MAX_ROWS)."""
    check_sql(sql)
    with connect(path) as conn:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description or []]
        rows = cur.fetchmany(MAX_ROWS)
    return {"columns": columns, "rows": rows, "truncated": len(rows) == MAX_ROWS}
