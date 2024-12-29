import streamlit as st
import pandas as pd
from db.database import get_connection
import datetime

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


def display_shoes_form():
    """
    Handle the daily entry for the Shoe Shop.
    """
    st.subheader("Shoe Shop Daily Entry")

    # Default to today's date
    date = st.date_input("Date for Shoe Shop Entry", value=pd.Timestamp.today())

    # Revenue input
    revenue = st.number_input("Enter Revenue (฿)", min_value=0, step=1)

    # Save entry
    if st.button("Save Shoe Shop Entry"):
        with get_connection() as conn:
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO daily_entries (date, shop, metric, value)
                    VALUES (?, ?, ?, ?)
                """, (date, 'Shoe Shop', 'Revenue', revenue))
                conn.commit()
                st.success(f"Shoe Shop revenue entry for {date} saved successfully!")
            except sqlite3.IntegrityError as e:
                st.error(f"Failed to save entry for {date}. Error: {str(e)}")


def display_barber_form():
    """
    Handle the daily entry for the Barber Shop.
    """
    st.subheader("Barber Shop Daily Entry")
    date = st.date_input("Date for Barber Shop Entry", value=pd.Timestamp.today())
    adult_haircuts = st.number_input("Adult Haircuts", min_value=0, step=1)
    child_haircuts = st.number_input("Child Haircuts", min_value=0, step=1)
    free_haircuts = st.number_input("Free Haircuts", min_value=0, step=1)

    if st.button("Save Barber Shop Entry"):
        with get_connection() as conn:
            try:
                conn.executemany("""
                    INSERT OR REPLACE INTO daily_entries (date, shop, metric, value)
                    VALUES (?, ?, ?, ?)
                """, [
                    (date, 'Barber Shop', 'Adult Haircuts', adult_haircuts),
                    (date, 'Barber Shop', 'Child Haircuts', child_haircuts),
                    (date, 'Barber Shop', 'Free Haircuts', free_haircuts)
                ])
                conn.commit()
                st.success(f"Barber Shop entries for {date} saved successfully!")
            except sqlite3.IntegrityError as e:
                st.error(f"Failed to save entries for {date}. Error: {str(e)}")


def display_meatball_form():
    """
    Data entry form for the Meatball Stand.
    """
    st.write("### Meatball Stand Daily Entry")

    # Default date to today
    today = datetime.date.today()

    # Form fields
    date = st.date_input("Date", value=st.session_state.get("entry_date", today))
    sales = st.number_input("Sales (฿)", min_value=0, step=1)
    salad_cost = st.number_input("Salad Cost (฿)", min_value=0, step=1)

    if st.button("Save Entry"):
        with get_connection() as conn:
            try:
                # Insert Sales
                conn.execute("""
                    INSERT INTO daily_entries (date, shop, metric, value)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(date, shop, metric)
                    DO UPDATE SET value = excluded.value
                """, (date, "Meatball Stand", "Sales", sales))

                # Insert Salad Cost
                conn.execute("""
                    INSERT INTO daily_entries (date, shop, metric, value)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(date, shop, metric)
                    DO UPDATE SET value = excluded.value
                """, (date, "Meatball Stand", "Salad Cost", salad_cost))

                conn.commit()
                st.success("Meatball Stand entry saved successfully!")
            except Exception as e:
                st.error(f"Error saving entry: {str(e)}")