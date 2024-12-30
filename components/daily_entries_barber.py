import streamlit as st
from db.database import get_connection
import pandas as pd

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
            except Exception as e:
                st.error(f"Failed to save entries for {date}. Error: {str(e)}")
