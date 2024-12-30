import streamlit as st

def update_account_in_db(account_id, name, balance, goal):
    # Mock function to simulate database update
    print(f"Account updated: ID={account_id}, Name={name}, Balance={balance}, Goal={goal}")

account = {"id": 1, "name": "Sample Account", "balance": 1000, "goal": 5000}

st.title("Edit Account")

with st.form(key='edit_form'):
    new_name = st.text_input("Account Name", value=account["name"])
    new_balance = st.number_input("Balance", value=account["balance"], min_value=0, step=1)
    new_goal = st.number_input("Goal", value=account["goal"], min_value=0, step=1)
    submit_button = st.form_submit_button(label='Save Changes')

if submit_button:
    update_account_in_db(account["id"], new_name, new_balance, new_goal)
    st.success(f"Account '{new_name}' updated successfully!")
