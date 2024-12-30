import streamlit as st
from components.daily_entries_barber import display_barber_form
from components.daily_entries_shoe import display_shoes_form
from components.daily_entries_meatball import display_meatball_form
from components.profit_report import display_profit_report

def display_daily_entries_menu():
    """
    Display the daily entries menu.
    """
    st.header("Daily Entries")
    shop = st.selectbox("Select Shop", ["Barber Shop", "Shoe Shop", "Meatball Shop"])

    if shop == "Barber Shop":
        display_barber_form()
    elif shop == "Shoe Shop":
        display_shoes_form()
    elif shop == "Meatball Shop":
        display_meatball_form()

    st.write("---")
    display_profit_report()
