import streamlit as st
from components.daily_entries import display_daily_entries_menu
from components.inventory import set_weekly_inventory
from components.reporting import generate_usage_report

def main():
    st.title("Business Tracker App")

    # Horizontal navigation menu
    menu = st.radio(
        "Navigation",
        ["Daily Entries", "Meatball Inventory", "Reports"],
        horizontal=True
    )

    # Render pages based on the selected menu item
    if menu == "Daily Entries":
        display_daily_entries_menu()
    elif menu == "Meatball Inventory":
        set_weekly_inventory()
    elif menu == "Reports":
        generate_usage_report()
    else:
        st.error("Invalid menu selection.")

if __name__ == "__main__":
    main()
