import sqlite3
import os
import requests
import sqlitecloud

# Connection details
SQLITECLOUD_URL = "sqlitecloud://cw3hlt0nnz.sqlite.cloud:8860?apikey=WcLJyCl3vRVS7mZaXIM6jXJSvKgAYBCvqfRItH6kmZA"

def get_connection():
    """
    Establish a connection to the SQLiteCloud database.
    """
    conn = sqlitecloud.connect(SQLITECLOUD_URL)
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
