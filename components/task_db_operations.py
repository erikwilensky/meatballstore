import sqlite3
from db.database import get_connection

def fetch_all_tasks():
    """
    Fetch all tasks from the database and convert them to dictionaries.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row  # Ensures rows are accessed as dictionaries
        rows = conn.execute(
            "SELECT id, name, description, deadline, status, parent_task FROM tasks"
        ).fetchall()
        return [dict(row) for row in rows]


def get_current_task(tasks):
    """
    Get the current main task from the list of tasks.
    """
    for task in tasks:
        if task["status"] == "Pending" and task["parent_task"] is None:
            return task
    return None


def add_task(name, description, deadline, parent_task_id=None):
    """
    Add a new task or subtask to the database.
    """
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tasks (name, description, deadline, status, parent_task)
            VALUES (?, ?, ?, 'Pending', ?)
            """,
            (name, description, deadline, parent_task_id),
        )
        conn.commit()


def complete_task(task_id):
    """
    Mark a task as completed in the database.
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,)
        )
        conn.commit()
