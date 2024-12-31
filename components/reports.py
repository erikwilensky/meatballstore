import pandas as pd
import streamlit as st
from datetime import date, timedelta
from database import get_connection
import plotly.express as px

def fetch_daily_data(selected_date):
    """Fetch daily profit data from database."""
    formatted_date = selected_date.strftime('%Y-%m-%d')
    previous_date = (selected_date - timedelta(days=1)).strftime('%Y-%m-%d')
    with get_connection() as conn:
        # Current day's data
        current_data = pd.read_sql_query("""
            SELECT shop, SUM(value) as profit
            FROM daily_entries
            WHERE date = ?
            GROUP BY shop
        """, conn, params=(formatted_date,))

        # Replace negative values with zero
        current_data['profit'] = current_data['profit'].apply(lambda x: max(x, 0))

        # Previous day's data
        previous_data = pd.read_sql_query("""
            SELECT shop, SUM(value) as profit
            FROM daily_entries
            WHERE date = ?
            GROUP BY shop
        """, conn, params=(previous_date,))

        # Replace negative values with zero
        previous_data['profit'] = previous_data['profit'].apply(lambda x: max(x, 0))

        return current_data, previous_data

def create_profit_chart(data):
    """Generate a pie chart or bar chart for profit data."""
    fig = px.pie(data, values='profit', names='shop', title='Profit Distribution')
    return fig

def display_profit_report():
    """Display the profit report."""
    try:
        selected_date = st.date_input("Select a date", value=date.today())
        current_data, previous_data = fetch_daily_data(selected_date)

        # Display profit charts
        st.subheader("Today's Profit Distribution")
        if not current_data.empty:
            st.plotly_chart(create_profit_chart(current_data), use_container_width=True)
        else:
            st.info("No data available to generate today's profit chart.")

        st.subheader("Yesterday's Profit Distribution")
        if not previous_data.empty:
            st.plotly_chart(create_profit_chart(previous_data), use_container_width=True)
        else:
            st.info("No data available to generate yesterday's profit chart.")

    except ValueError as e:
        st.error(f"Value Error: {str(e)}")
    except KeyError as e:
        st.error(f"Key Error: Missing column {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
