import streamlit as st
import pandas as pd
from datetime import date
from db.database import get_connection

def reports():
    st.title("Reports")

    # Select date for the report, defaulting to today
    report_date = st.date_input("Select Report Date", value=date.today())

    try:
        with get_connection() as conn:
            # Retrieve data grouped by shop
            data = pd.read_sql_query("""
                SELECT shop, SUM(value) AS profit
                FROM daily_entries
                WHERE date = ?
                GROUP BY shop
            """, conn, params=(report_date,))

        if data.empty:
            st.write("No data found for the selected date.")
            return

        # Summarize profits
        st.subheader("Profit Summary")
        for index, row in data.iterrows():
            st.write(f"{row['shop']}: Profit = ฿{row['profit']}")

        # Plot profits
        st.subheader("Profit by Shop")
        data.set_index("shop", inplace=True)
        data["profit"].plot(kind="bar", title=f"Profit Report for {report_date}")
        st.pyplot()
    except Exception as e:
        st.error(f"Error generating report: {e}")
