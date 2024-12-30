import streamlit as st
from db.database import get_connection
import sqlite3
import math


def create_heart_progress_bar(current, goal, num_hearts=10):
    """
    Create a progress bar made of hearts showing progress towards goal.
    Returns filled hearts and empty hearts as strings.
    """
    if goal <= 0:
        return "❤️" * num_hearts, "🤍" * 0  # All filled if no goal

    progress = min(current / goal, 1.0)  # Cap at 100%
    filled_hearts = math.floor(progress * num_hearts)
    empty_hearts = num_hearts - filled_hearts

    return "❤️" * filled_hearts, "🤍" * empty_hearts


def fetch_all_accounts():
    """
    Fetch all accounts from the database.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT * FROM accounts").fetchall()


def update_account_in_db(account_id, name, balance, goal):
    """
    Update an account in the database.
    """
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE accounts
            SET name = ?, balance = ?, goal = ?
            WHERE id = ?
            """,
            (name, balance, goal, account_id),
        )
        conn.commit()


def delete_account_from_db(account_id):
    """
    Delete an account from the database.
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        conn.commit()


def display_accounts_page():
    st.title("Accounts Management")

    # Initialize session state for editing
    if "editing_account_id" not in st.session_state:
        st.session_state.editing_account_id = None

    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False

    # Add Account button
    if st.button("➕ Add New Account"):
        st.session_state.show_add_form = True
        st.session_state.editing_account_id = None
        st.rerun()

    # Fetch and display all accounts
    accounts = fetch_all_accounts()

    if not accounts:
        st.info("No accounts available. Add one below!")
        st.session_state.show_add_form = True
    else:
        # Create tabs for accounts overview and individual accounts
        tabs = ["Overview"] + [account["name"] for account in accounts]
        active_tab = st.tabs(tabs)

        # Overview Tab
        with active_tab[0]:
            st.subheader("All Accounts Summary")
            total_balance = sum(account["balance"] for account in accounts)
            total_goals = sum(account["goal"] for account in accounts)

            st.metric("Total Balance", f"฿{total_balance:,.2f}")
            if total_goals > 0:
                overall_progress = (total_balance / total_goals) * 100
                st.metric("Overall Progress", f"{overall_progress:.1f}%")

            st.markdown("---")
            st.caption("Quick view of all accounts:")
            for account in accounts:
                filled, empty = create_heart_progress_bar(account["balance"], account["goal"])
                progress_text = f"{(account['balance'] / account['goal'] * 100):.1f}%" if account[
                                                                                              "goal"] > 0 else "No Goal Set"
                st.markdown(f"**{account['name']}**: {filled}{empty} ({progress_text})")

        # Individual Account Tabs
        for i, account in enumerate(accounts, 1):
            with active_tab[i]:
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.subheader(account["name"])
                with col2:
                    st.markdown("###")  # Spacing
                    if st.button("✏️ Edit", key=f"edit_{account['id']}"):
                        st.session_state.editing_account_id = account['id']
                        st.session_state.show_add_form = False
                        st.rerun()

                # Display account details
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Balance", f"฿{account['balance']:,.2f}")
                with col2:
                    st.metric("Goal Amount", f"฿{account['goal']:,.2f}")

                # Progress bar with hearts
                filled_hearts, empty_hearts = create_heart_progress_bar(account["balance"], account["goal"])
                st.write("Progress towards goal:")
                st.markdown(f"<h2 style='text-align: center'>{filled_hearts}{empty_hearts}</h2>",
                            unsafe_allow_html=True)

                if account["goal"] > 0:
                    progress = (account["balance"] / account["goal"]) * 100
                    remaining = account["goal"] - account["balance"]
                    st.markdown(f"""
                        - Progress: **{progress:.1f}%**
                        - Remaining: **฿{remaining:,.2f}**
                    """)

                # Delete button at bottom
                if st.button("🗑️ Delete Account", key=f"delete_{account['id']}"):
                    if st.warning("Are you sure you want to delete this account?"):
                        delete_account_from_db(account["id"])
                        st.rerun()

                # Show edit form if this account is being edited
                if st.session_state.editing_account_id == account['id']:
                    st.markdown("---")
                    display_edit_account_form(account)

    # Show add form if requested
    if st.session_state.show_add_form:
        st.markdown("---")
        display_add_account_form()


def display_add_account_form():
    """
    Display a form to add a new account.
    """
    st.subheader("➕ Add New Account")
    with st.form(key="add_account_form"):
        account_name = st.text_input("Account Name")
        initial_balance = st.number_input("Initial Balance (฿)", min_value=0.0, step=100.0)
        goal_amount = st.number_input("Goal Amount (฿)", min_value=0.0, step=100.0)

        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Add Account")
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_add_form = False
                st.rerun()

        if submitted:
            if account_name:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO accounts (name, balance, goal)
                        VALUES (?, ?, ?)
                        """,
                        (account_name, initial_balance, goal_amount),
                    )
                    conn.commit()
                st.success(f"Account '{account_name}' added successfully!")
                st.session_state.show_add_form = False
                st.rerun()
            else:
                st.warning("Account name cannot be empty.")


def display_edit_account_form(account):
    """
    Display a form to edit an existing account.
    """
    st.subheader(f"✏️ Edit Account: {account['name']}")
    with st.form(key=f"edit_form_{account['id']}"):
        new_name = st.text_input("Account Name", value=account["name"])
        new_balance = st.number_input("Current Balance (฿)", value=float(account["balance"]), min_value=0.0, step=100.0)
        new_goal = st.number_input("Goal Amount (฿)", value=float(account["goal"]), min_value=0.0, step=100.0)

        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.editing_account_id = None
                st.rerun()

        if submitted:
            update_account_in_db(account["id"], new_name, new_balance, new_goal)
            st.success(f"Account '{new_name}' updated successfully!")
            st.session_state.editing_account_id = None
            st.rerun()