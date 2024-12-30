import streamlit as st
from db.database import get_connection
import datetime

def display_meatball_form():
    """
    Data entry form for the Meatball Stand.
    """
    st.subheader("Meatball Stand Daily Entry")
    today = datetime.date.today()
    date = st.date_input("Date", value=today)
    sales = st.number_input("Sales (฿)", min_value=0, step=1)
    salad_cost = st.number_input("Salad Cost (฿)", min_value=0, step=1)

    if st.button("Save Entry"):
        with get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO daily_entries (date, shop, metric, value)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(date, shop, metric)
                    DO UPDATE SET value = excluded.value
                """, (date, "Meatball Stand", "Sales", sales))

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
