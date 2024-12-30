from db.database import get_connection
from datetime import datetime, date
import sqlite3
import streamlit as st
from components.accounts import display_accounts_page
from components.task_page import task_map_page  # Main task management page

def display_move_forward_menu():
    """Display Move Forward menu."""
    st.subheader("Move Forward!")
    menu = st.radio("Select an Option", ["Task Map", "Accounts"], horizontal=True)

    if menu == "Task Map":
        task_map_page()  # Use the main task management function
    elif menu == "Accounts":
        display_accounts_page()
