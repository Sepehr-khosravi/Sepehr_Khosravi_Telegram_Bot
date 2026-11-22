import os
import sys
import sqlite3
import tempfile
import pytest

# Make project root importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    """
    Point database.DB_PATH at a temp file for this test,
    and initialize the schema. Each test gets a clean DB.
    """
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    database.init_db()
    yield str(db_file)
    # tmp_path cleans itself up