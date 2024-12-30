from db.database import get_connection

def list_tables():
    with get_connection() as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        for table in tables:
            print(table["name"])

list_tables()