import sqlite3
from pathlib import Path

DB_PATH = Path("data/archive.db")
MAX_BODY_CHARS = 1200
MAX_SUMMARY_CHARS = 900

def column_exists(conn, table, column):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)

def main():
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)

    if column_exists(conn, "news_articles", "body_excerpt"):
        conn.execute(
            """
            UPDATE news_articles
            SET body_excerpt = substr(body_excerpt, 1, ?)
            WHERE body_excerpt IS NOT NULL AND length(body_excerpt) > ?
            """,
            (MAX_BODY_CHARS, MAX_BODY_CHARS),
        )

    if column_exists(conn, "news_articles", "summary"):
        conn.execute(
            """
            UPDATE news_articles
            SET summary = substr(summary, 1, ?)
            WHERE summary IS NOT NULL AND length(summary) > ?
            """,
            (MAX_SUMMARY_CHARS, MAX_SUMMARY_CHARS),
        )

    conn.execute("VACUUM")
    conn.commit()
    conn.close()

    print("Archive compacted.")

if __name__ == "__main__":
    main()
