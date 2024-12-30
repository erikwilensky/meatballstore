import sqlite3
from database import get_connection

def test_update_account():
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE accounts
            SET name = ?, balance = ?, goal = ?
            WHERE id = ?
            """,
            ("Updated Account", 5000, 10000, 1),  # Example: Update account with ID 1
        )
        conn.commit()

    # Fetch the updated account to verify
    with get_connection() as conn:
        updated_account = conn.execute("SELECT * FROM accounts WHERE id = ?", (1,)).fetchone()
        print("Updated Account:", updated_account)

test_update_account()
