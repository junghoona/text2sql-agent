"""Safety-guard tests: pytest"""
import sqlite3

import pytest

from t2s import db


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT, updated_at TEXT)")
        conn.executemany("INSERT INTO users VALUES (?, ?, ?)", [(i, f"u{i}", "2024") for i in range(300)])
    return str(path)


@pytest.mark.parametrize("sql", [
    "SELECT * FROM users",
    "select name, updated_at from users;",
    "WITH t AS (SELECT id FROM users) SELECT COUNT(*) FROM t",
])
def test_allows_selects(sql):
    db.check_sql(sql)


@pytest.mark.parametrize("sql", [
    "", "DROP TABLE users", "DELETE FROM users", "UPDATE users SET name='x'",
    "INSERT INTO users VALUES (1,'a','b')", "SELECT 1; DROP TABLE users",
    "PRAGMA table_info(users)", "ATTACH DATABASE 'x.db' AS x",
])
def test_blocks_unsafe(sql):
    with pytest.raises(ValueError):
        db.check_sql(sql)


def test_run_query_caps_rows(db_path):
    result = db.run_query("SELECT * FROM users", path=db_path)
    assert result["columns"] == ["id", "name", "updated_at"]
    assert len(result["rows"]) == db.MAX_ROWS and result["truncated"]


def test_connection_is_read_only(db_path):
    with pytest.raises(sqlite3.OperationalError):
        db.connect(db_path).execute("DELETE FROM users")


def test_schema_lists_tables(db_path):
    assert "users: 300 rows" in db.get_schema(db_path)
