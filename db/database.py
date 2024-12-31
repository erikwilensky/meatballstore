import sqlite3
import os
import requests

# Google Drive upload link for your file
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files/1CI6zLUicS0MaR2iP9TyDQ_Udjq_QF8Q_?uploadType=media"

# OAuth 2.0 Bearer Token (replace with your token if needed)
ACCESS_TOKEN = "your_oauth_token_here"

def upload_database():
    """
    Upload the updated SQLite database to Google Drive.
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream",
    }
    with open(DB_FILE, "rb") as file:
        response = requests.patch(UPLOAD_URL, headers=headers, data=file)
    if response.status_code == 200:
        print("Database uploaded successfully.")
    else:
        print(f"Failed to upload database. Status code: {response.status_code}")
        print(response.json())

# End of new code

# Public URL for the SQLite database file on Google Drive
DB_URL = "https://drive.google.com/uc?export=download&id=1CI6zLUicS0MaR2iP9TyDQ_Udjq_QF8Q_"

# Local path for the database file
DB_FILE = "business_tracker.db"

# Download the database if it doesn't exist locally
if not os.path.exists(DB_FILE):
    print("Database file not found locally. Downloading from Google Drive...")
    response = requests.get(DB_URL)
    if response.status_code == 200:
        with open(DB_FILE, "wb") as file:
            file.write(response.content)
        print("Database downloaded successfully.")
    else:
        raise Exception(f"Failed to download database file. Status code: {response.status_code}")

def get_connection():
    """
    Establish a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Rows are accessible as dictionaries
    return conn

def setup_database():
    """
    Create necessary tables if they do not exist.
    """
    with get_connection() as conn:
        # Create table for daily entries
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                shop TEXT NOT NULL,
                metric TEXT NOT NULL,
                value INTEGER NOT NULL,
                UNIQUE(date, shop, metric)
            )
        """)

        # Create table for inventory items
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cost INTEGER NOT NULL,
                quantity REAL DEFAULT 0 NOT NULL,
                UNIQUE(name)
            )
        """)

        # Create table for weekly inventory records
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weekly_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                inventory_type TEXT NOT NULL CHECK (inventory_type IN ('start', 'end')),
                quantity REAL NOT NULL,
                record_date TEXT NOT NULL,
                week_number INTEGER NOT NULL,
                year INTEGER NOT NULL,
                FOREIGN KEY (item_id) REFERENCES inventory_items (id),
                UNIQUE(item_id, inventory_type, week_number, year)
            )
        """)

        # Create table for weekly tracking completeness
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weekly_tracking (
                week_number INTEGER NOT NULL,
                year INTEGER NOT NULL,
                start_inventory BOOLEAN NOT NULL DEFAULT 0,
                end_inventory BOOLEAN NOT NULL DEFAULT 0,
                UNIQUE(week_number, year)
            )
        """)

        # Create table for tasks
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                parent_task INTEGER DEFAULT NULL,
                FOREIGN KEY (parent_task) REFERENCES tasks (id)
            )
        """)

        # Create table for accounts
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance INTEGER NOT NULL,
                goal INTEGER NOT NULL,
                UNIQUE(name)
            )
        """)

        conn.commit()

def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    Use this function to start fresh.
    """
    with get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS daily_entries;")
        conn.execute("DROP TABLE IF EXISTS inventory_items;")
        conn.execute("DROP TABLE IF EXISTS weekly_inventory;")
        conn.execute("DROP TABLE IF EXISTS weekly_tracking;")
        conn.execute("DROP TABLE IF EXISTS tasks;")
        conn.execute("DROP TABLE IF EXISTS accounts;")
        conn.commit()
    setup_database()
