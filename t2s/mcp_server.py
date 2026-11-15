"""Stretch goal: expose the same DB over MCP (stdio). Run: python -m t2s.mcp_server"""
import json

from mcp.server.mcpserver import MCPServer

from t2s import db

mcp = MCPServer("text2sql")


@mcp.tool()
def get_schema() -> str:
    """Return the database schema (CREATE TABLE statements + row counts)."""
    return db.get_schema()


@mcp.tool()
def run_sql(sql: str) -> str:
    """Run a single read-only SELECT query and return JSON results."""
    return json.dumps(db.run_query(sql), default=str)


if __name__ == "__main__":
    mcp.run()
