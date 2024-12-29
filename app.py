import streamlit as st
from pathlib import Path
from components.daily_entries import display_daily_entries_menu
from components.inventory import display_meatball_inventory
from components.reporting import generate_usage_report

def main():
    # Set page configuration
    st.set_page_config(page_title="Oy Companies Data System", layout="wide")

    # Inject custom CSS for larger font
    inject_custom_css()

    # Title
    st.title("Oy Companies Data System")

    # Horizontal menu for navigation
    menu = st.radio(
        "Navigate:",
        ["Daily Entries", "Meatball Inventory", "Reports"],
        horizontal=True
    )

    # Navigation logic
    if menu == "Daily Entries":
        display_daily_entries_menu()
    elif menu == "Meatball Inventory":
        display_meatball_inventory()
    elif menu == "Reports":
        generate_usage_report()
    else:
        st.error("Invalid menu selection.")

def inject_custom_css():
    """Inject custom CSS into the app."""
    css_file = Path("style.css")
    if css_file.exists():
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
