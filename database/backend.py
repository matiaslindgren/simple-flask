"""
Database backend - SQLite interface.
"""
import functools
import os
import sqlite3


SQL_SCHEMA = """
DROP TABLE IF EXISTS messages;
CREATE TABLE messages (
  id       integer  primary key autoincrement,
  title    text,
  content  text,
  sender   text,
  url      text
);
"""

DATABASE_PATH = os.path.join(os.environ["DATABASE_DIR"], "messages.sqlite3.db")


def with_db_cursor(*, commit):
    def wrapper(cursor_func):
        @functools.wraps(cursor_func)
        def connect_execute_commit(*args, **kwargs):
            connection = sqlite3.connect(DATABASE_PATH)
            connection.row_factory = sqlite3.Row
            result = cursor_func(connection.cursor(), *args, **kwargs)
            if commit:
                connection.commit()
            return result
            connection.close()
        return connect_execute_commit
    return wrapper


@with_db_cursor(commit=True)
def reset_table(cursor):
    cursor.executescript(SQL_SCHEMA.strip())


@with_db_cursor(commit=True)
def create_message(cursor, title, content, sender, url):
    cursor.execute(
        "INSERT INTO messages (title, content, sender, url) VALUES (?, ?, ?, ?)",
        (title, content, sender, url))
    cursor.execute("SELECT * FROM messages WHERE id=?", (cursor.lastrowid,))
    return cursor.fetchone()[0]


@with_db_cursor(commit=False)
def get_all_messages(cursor):
    cursor.execute("SELECT * FROM messages")
    return [dict(row) for row in cursor.fetchall()]
