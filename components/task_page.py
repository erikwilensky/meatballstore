import sqlite3
import streamlit as st
from db.database import get_connection
from datetime import datetime, date
import graphviz


def delete_task_with_confirmation(task):
    """
    Display a confirmation message before deleting a task and its subtasks.
    """
    st.warning(f"Are you sure you want to delete **{task['name']}** and all its subtasks?")

    # Confirmation button
    if st.button(f"Confirm Delete {task['name']}", key=f"confirm_delete_{task['id']}"):
        delete_task(task["id"])
        st.success(f"Task '{task['name']}' and all its subtasks have been deleted!")
        st.session_state["tasks_updated"] = True  # Mark tasks as updated


def task_map_page():
    """
    Main Task Map Page to display and manage tasks.
    """
    st.subheader("Task Map")

    # Fetch all tasks
    tasks = fetch_all_tasks()

    # Identify the current task
    current_task = get_current_task(tasks)

    if current_task:
        display_current_task(current_task)
    else:
        st.info("No current task. Add a new main task below.")

    # Toggle to show or hide the main task form
    if "show_main_task_form" not in st.session_state:
        st.session_state["show_main_task_form"] = False

    if not st.session_state["show_main_task_form"]:
        if st.button("Add Main Task"):
            st.session_state["show_main_task_form"] = True

    if st.session_state["show_main_task_form"]:
        display_add_main_task_form()

    # Task Hierarchy Visualization
    st.write("---")
    st.subheader("Task Hierarchy Visualization")
    display_task_graph(tasks)

    # Task List with Actions
    st.write("---")
    st.subheader("Manage Tasks")
    display_task_list_with_actions(tasks)


def display_task_graph(tasks):
    """
    Display tasks and subtasks in a graph form using Graphviz.
    """
    graph = graphviz.Digraph(format="svg")
    graph.attr(rankdir="LR")  # Arrange the graph from left to right

    for task in tasks:
        # Add nodes for tasks
        graph.node(str(task["id"]), f'{task["name"]}\n({task["deadline"]})')

        # Add edges for subtasks
        if task["parent_task"]:
            graph.edge(str(task["parent_task"]), str(task["id"]))

    # Display the graph
    st.graphviz_chart(graph)


def delete_task(task_id):
    """
    Delete a task and all its subtasks from the database.
    """
    with get_connection() as conn:
        # Fetch all child tasks of the task to be deleted
        child_tasks = conn.execute(
            "SELECT id FROM tasks WHERE parent_task = ?", (task_id,)
        ).fetchall()

        # Recursively delete child tasks
        for child in child_tasks:
            delete_task(child["id"])  # Recursive call to delete child tasks

        # Delete the parent task itself
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()


def display_task_list_with_actions(tasks):
    """
    Display tasks as a list with options to edit, delete, and add subtasks.
    """
    for task in tasks:
        # Display task details in a single expander
        with st.expander(f"{task['name']} ({task['deadline']})"):
            st.write(f"**Description:** {task['description']}")
            st.write(f"**Status:** {task['status']}")

            # Buttons for editing and deleting tasks
            if st.button(f"Edit {task['name']}", key=f"edit_{task['id']}"):
                display_edit_task_form(task)

            # Call delete_task_with_confirmation without nesting
            delete_task_with_confirmation(task)

            # Add Subtask Form
            if st.button(f"Add Subtask to {task['name']}", key=f"add_subtask_{task['id']}"):
                st.session_state[f"show_subtask_form_{task['id']}"] = True

            if st.session_state.get(f"show_subtask_form_{task['id']}"):
                with st.form(f"subtask_form_{task['id']}"):
                    subtask_name = st.text_input("Subtask Name", key=f"subtask_name_{task['id']}")
                    subtask_description = st.text_area("Subtask Description", key=f"subtask_desc_{task['id']}")
                    subtask_deadline = st.date_input("Subtask Deadline", key=f"subtask_deadline_{task['id']}")
                    if st.form_submit_button("Add Subtask"):
                        add_task(subtask_name, subtask_description, subtask_deadline, task["id"])
                        st.session_state[f"show_subtask_form_{task['id']}"] = False
                        st.session_state["tasks_updated"] = True

    # Check for task updates
    if st.session_state.get("tasks_updated", False):
        st.session_state["tasks_updated"] = False
        tasks = fetch_all_tasks()  # Reload tasks to reflect updates






def display_current_task(task):
    """
    Display the current main task.
    """
    st.markdown(f"### Current Task: {task['name']}")
    st.markdown(task['description'])
    st.markdown(f"**Deadline:** {task['deadline']}")

    today = date.today()
    deadline_date = datetime.strptime(task['deadline'], "%Y-%m-%d").date()
    remaining_days = (deadline_date - today).days

    if remaining_days >= 0:
        st.info(f"{remaining_days} days remaining.")
    else:
        st.error("Deadline has passed.")

    # Button to mark the task as completed
    if st.button("Mark Task as Completed", key=f"complete_task_{task['id']}"):
        complete_task(task['id'])
        st.experimental_rerun()


def display_add_main_task_form():
    """
    Display a form to add a new main task.
    """
    st.markdown("### Add Main Task")
    with st.form("add_main_task_form"):
        name = st.text_input("Task Name")
        description = st.text_area("Task Description")
        deadline = st.date_input("Deadline")
        submitted = st.form_submit_button("Add Task")

        if submitted:
            if not name or not description:
                st.warning("Task Name and Description cannot be empty.")
            else:
                add_task(name, description, deadline)
                st.success("Main task added successfully!")
                st.session_state.show_main_task_form = False
                st.experimental_rerun()


def display_edit_task_form(task):
    """
    Display a form to edit an existing task.
    """
    st.markdown(f"### Edit Task: {task['name']}")
    with st.form(f"edit_task_form_{task['id']}"):
        new_name = st.text_input("Task Name", value=task['name'])
        new_description = st.text_area("Task Description", value=task['description'])
        new_deadline = st.date_input("Deadline", value=datetime.strptime(task['deadline'], "%Y-%m-%d").date())
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if not new_name or not new_description:
                st.warning("Task Name and Description cannot be empty.")
            else:
                update_task(task['id'], new_name, new_description, new_deadline)
                st.success(f"Task '{new_name}' updated successfully!")
                st.experimental_rerun()


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


def update_task(task_id, name, description, deadline):
    """
    Update an existing task in the database.
    """
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET name = ?, description = ?, deadline = ?
            WHERE id = ?
            """,
            (name, description, deadline, task_id),
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


def delete_task(task_id):
    """
    Delete a task and all its subtasks from the database.
    """
    with get_connection() as conn:
        # Fetch all child tasks of the task to be deleted
        child_tasks = conn.execute(
            "SELECT id FROM tasks WHERE parent_task = ?", (task_id,)
        ).fetchall()

        # Recursively delete child tasks
        for child in child_tasks:
            delete_task(child["id"])  # Recursive call to delete child tasks

        # Delete the parent task itself
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()



def fetch_all_tasks():
    """
    Fetch all tasks from the database.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT id, name, description, deadline, status, parent_task FROM tasks"
        ).fetchall()


def get_current_task(tasks):
    """
    Get the current main task from the list of tasks.
    """
    for task in tasks:
        if task["status"] == "Pending" and task["parent_task"] is None:
            return task
    return None
