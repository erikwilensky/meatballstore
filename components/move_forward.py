import streamlit as st
from db.database import get_connection
from datetime import datetime, date  # Importing datetime and date modules

def edit_account_form(account):
    """
    Display a form to edit an existing account.
    """
    st.write(f"### Edit Account: {account['name']}")
    with st.form(f"edit_account_form_{account['id']}"):
        new_name = st.text_input("Account Name", value=account['name'])
        new_balance = st.number_input("Current Balance (฿)", value=account['balance'], min_value=0, step=1)
        new_goal = st.number_input("Goal (฿)", value=account['goal'], min_value=0, step=1)
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            with get_connection() as conn:
                try:
                    conn.execute("""
                        UPDATE accounts
                        SET name = ?, balance = ?, goal = ?
                        WHERE id = ?
                    """, (new_name, new_balance, new_goal, account['id']))
                    conn.commit()
                    st.success(f"Account '{new_name}' updated successfully!")
                except Exception as e:
                    st.error(f"Error updating account: {str(e)}")


def display_move_forward_menu():
    """
    Display Move Forward! menu with Next Task and Accounts options.
    """
    st.subheader("Move Forward!")
    menu = st.radio(
        "Select an Option",
        ["Next Task", "Accounts"],
        horizontal=True
    )

    if menu == "Next Task":
        next_task_page()
    elif menu == "Accounts":
        accounts_page()

def next_task_page():
    """
    Display the current task or allow the user to add a new task.
    """
    st.subheader("Next Task")

    # Fetch the current task
    with get_connection() as conn:
        task = conn.execute("SELECT * FROM tasks LIMIT 1").fetchone()

    if task:
        task_name = task["name"]
        description = task["description"]
        due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        today = date.today()

        # Calculate progress toward deadline
        total_days = (due_date - today).days
        elapsed_days = (total_days if total_days > 0 else 0)
        progress = min(max(100 - int((elapsed_days / total_days) * 100), 0), 100) if total_days > 0 else 100

        # Display task information
        st.markdown(f"### **{task_name}**")
        st.markdown(description)
        st.markdown(f"**Due Date:** {due_date}")

        # Deadline Progress Indicator
        st.progress(progress / 100)
        if progress < 100:
            st.info(f"{total_days} days remaining.")
        else:
            st.error("Deadline has passed.")

        # Delete task option
        if st.button("Delete Task"):
            with get_connection() as conn:
                conn.execute("DELETE FROM tasks WHERE id = ?", (task["id"],))
                conn.commit()
            st.success("Task deleted successfully!")
            st.session_state["task_mode"] = "create"  # Reset to create mode
    else:
        st.info("No task available. Add a new task below.")

        # Task creation form
        with st.form("task_form"):
            task_name = st.text_input("Task Name")
            description = st.text_area("Description")
            due_date = st.date_input("Due Date")
            submitted = st.form_submit_button("Save Task")

            if submitted:
                if not task_name or not description:
                    st.warning("Task Name and Description cannot be empty.")
                else:
                    with get_connection() as conn:
                        conn.execute("""
                            INSERT INTO tasks (name, description, due_date)
                            VALUES (?, ?, ?)
                        """, (task_name, description, due_date))
                        conn.commit()
                    st.success("Task saved successfully!")
                    st.session_state["task_mode"] = "view"  # Switch to view mode


def edit_task_form(task):
    """
    Display a form to edit the current task.
    """
    st.write("### Edit Task")
    with st.form("edit_task_form"):
        task_name = st.text_input("Task Name", value=task['name'])
        task_description = st.text_area("Description", value=task['description'])
        task_due_date = st.date_input("Due Date", value=task['due_date'])
        submitted = st.form_submit_button("Update Task")

        if submitted:
            with get_connection() as conn:

                conn.execute("""
                    UPDATE tasks
                    SET name = ?, description = ?, due_date = ?
                    WHERE id = ?
                """, (task_name, task_description, task_due_date,  task['id']))
                conn.commit()
                st.success("Task updated successfully!")


def accounts_page():
    """
    Display and manage extra money accounts.
    """
    st.subheader("Accounts")

    # Fetch accounts from the database
    with get_connection() as conn:
        accounts = conn.execute("SELECT * FROM accounts").fetchall()

    if accounts:
        for account in accounts:
            account_id = account["id"]
            name = account["name"]
            balance = account["balance"]
            goal = account["goal"]

            st.markdown(f"### {name}")
            st.markdown(f"**Balance:** ฿{balance}")
            st.markdown(f"**Goal:** ฿{goal}")

            # Calculate and display progress
            progress = min(balance / goal, 1.0)  # Ensure value is between 0.0 and 1.0
            st.progress(progress)
            st.markdown(f"**Progress:** {progress * 100:.2f}%")

            # Buttons for adding/removing funds
            col1, col2, col3 = st.columns(3)
            with col1:
                add_amount = st.number_input(f"Add Amount to {name}", min_value=0, step=1, key=f"add_{account_id}")
                if st.button(f"Add to {name}", key=f"btn_add_{account_id}"):
                    with get_connection() as conn:
                        conn.execute("""
                            UPDATE accounts
                            SET balance = balance + ?
                            WHERE id = ?
                        """, (add_amount, account_id))
                        conn.commit()
                    st.success(f"Added ฿{add_amount} to {name}!")

            with col2:
                remove_amount = st.number_input(f"Remove Amount from {name}", min_value=0, step=1, key=f"remove_{account_id}")
                if st.button(f"Remove from {name}", key=f"btn_remove_{account_id}"):
                    if remove_amount > balance:
                        st.warning("Cannot remove more than the current balance.")
                    else:
                        with get_connection() as conn:
                            conn.execute("""
                                UPDATE accounts
                                SET balance = balance - ?
                                WHERE id = ?
                            """, (remove_amount, account_id))
                            conn.commit()
                        st.success(f"Removed ฿{remove_amount} from {name}!")

            with col3:
                if st.button(f"Delete {name}", key=f"btn_delete_{account_id}"):
                    with get_connection() as conn:
                        conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
                        conn.commit()
                    st.success(f"Deleted account: {name}")

            st.write("---")
    else:
        st.info("No accounts found. Add a new account below.")

    # Add new account form
    with st.expander("Add New Account"):
        account_name = st.text_input("Account Name")
        initial_balance = st.number_input("Initial Balance (฿)", min_value=0, step=1)
        goal_amount = st.number_input("Goal Amount (฿)", min_value=0, step=1)
        if st.button("Add Account"):
            if account_name:
                with get_connection() as conn:
                    conn.execute("""
                        INSERT INTO accounts (name, balance, goal)
                        VALUES (?, ?, ?)
                    """, (account_name, initial_balance, goal_amount))
                    conn.commit()
                st.success(f"Added new account: {account_name}")
            else:
                st.warning("Account name cannot be empty.")