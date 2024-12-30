import streamlit as st
from db.database import get_connection
import pandas as pd

def display_shoes_form():
    """
    Handle the daily entry for the Shoe Shop.
    """
    st.subheader("Shoe Shop Daily Entry")
    date = st.date_input("Date for Shoe Shop Entry", value=pd.Timestamp.today())
    revenue = st.number_input("Enter Revenue (฿)", min_value=0, step=1)

    if st.button("Save Shoe Shop Entry"):
        with get_connection() as conn:
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO daily_entries (date, shop, metric, value)
                    VALUES (?, ?, ?, ?)
                """, (date, 'Shoe Shop', 'Revenue', revenue))
                conn.commit()
                st.success(f"Shoe Shop revenue entry for {date} saved successfully!")
            except Exception as e:
                st.error(f"Failed to save entry for {date}. Error: {str(e)}")
