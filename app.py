
import streamlit as st
from pathlib import Path
from components.daily_entries import display_daily_entries_menu
from components.inventory import display_meatball_inventory
from components.reporting import generate_usage_report
from components.move_forward import display_move_forward_menu
from db.database import setup_database






def main():
    setup_database()

    # Set page configuration
    st.set_page_config(page_title="Oy Companies Data System", layout="wide")

    # Inject custom CSS for larger font
    inject_custom_css()

    # Title
    st.title("Oy Companies Data System")

    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Daily Entries"):
            st.session_state["current_page"] = "Daily Entries"
    with col2:
        if st.button("Meatball Inventory"):
            st.session_state["current_page"] = "Meatball Inventory"
    with col3:
        if st.button("Reports"):
            st.session_state["current_page"] = "Reports"
    with col4:
        if st.button("Move Forward!"):
            st.session_state["current_page"] = "Move Forward!"

    # Default page setting
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Daily Entries"

    # Navigation logic
    if st.session_state["current_page"] == "Daily Entries":
        display_daily_entries_menu()
    elif st.session_state["current_page"] == "Meatball Inventory":
        display_meatball_inventory()
    elif st.session_state["current_page"] == "Reports":
        generate_usage_report()
    elif st.session_state["current_page"] == "Move Forward!":
        display_move_forward_menu()
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
