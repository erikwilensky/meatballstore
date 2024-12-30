


import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
from db.database import get_connection


def calculate_growth(current, previous):
    """Calculate percentage growth between two values."""
    if previous == 0:
        return 0
    return ((current - previous) / abs(previous)) * 100


def fetch_daily_data(selected_date):
    """Fetch daily profit data from database."""
    with get_connection() as conn:
        # Current day's data
        current_data = pd.read_sql_query("""
            SELECT shop, SUM(value) as profit
            FROM daily_entries
            WHERE date = ?
            GROUP BY shop
        """, conn, params=(selected_date,))

        # Previous day's data
        previous_data = pd.read_sql_query("""
            SELECT shop, SUM(value) as profit
            FROM daily_entries
            WHERE date = ?
            GROUP BY shop
        """, conn, params=(selected_date - timedelta(days=1),))

        return current_data, previous_data


def fetch_weekly_trend(end_date):
    """Fetch weekly trend data."""
    start_date = end_date - timedelta(days=6)
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT date, shop, SUM(value) as profit
            FROM daily_entries
            WHERE date BETWEEN ? AND ?
            GROUP BY date, shop
        """, conn, params=(start_date, end_date))


def display_metrics_cards(current_data, previous_data):
    """Display metric cards with daily comparisons."""
    total_current = current_data['profit'].sum()
    total_previous = previous_data['profit'].sum() if not previous_data.empty else 0
    growth = calculate_growth(total_current, total_previous)

    cols = st.columns(3)

    # Total Daily Profit
    with cols[0]:
        st.metric(
            "Total Daily Profit",
            f"฿{total_current:,.2f}",
            f"{growth:+.1f}% vs yesterday",
            delta_color="normal"
        )

    # Average Profit per Shop
    avg_profit = total_current / len(current_data) if len(current_data) > 0 else 0
    with cols[1]:
        st.metric(
            "Average Profit per Shop",
            f"฿{avg_profit:,.2f}",
            f"{len(current_data)} active shops"
        )

    # Best Performing Shop
    if not current_data.empty:
        best_shop = current_data.loc[current_data['profit'].idxmax()]
        with cols[2]:
            st.metric(
                "Best Performing Shop",
                best_shop['shop'],
                f"฿{best_shop['profit']:,.2f}"
            )


def create_profit_chart(data):
    """Create an interactive bar chart for profits."""
    fig = px.bar(
        data,
        x='shop',
        y='profit',
        title='Daily Profit by Shop',
        labels={'shop': 'Shop Name', 'profit': 'Profit (฿)'},
        color='profit',
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        height=400,
        xaxis_title="Shop",
        yaxis_title="Profit (฿)",
        showlegend=False,
        hovermode='x'
    )

    return fig


def create_weekly_trend_chart(data):
    """Create a line chart for weekly trends."""
    fig = px.line(
        data,
        x='date',
        y='profit',
        color='shop',
        title='Weekly Profit Trends',
        labels={'date': 'Date', 'profit': 'Profit (฿)', 'shop': 'Shop'}
    )

    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Profit (฿)",
        hovermode='x unified'
    )

    return fig


def reports():
    """Main reports page."""
    st.title("📊 Financial Reports Dashboard")

    # Date selector with custom styling
    col1, col2 = st.columns([2, 1])
    with col1:
        report_date = st.date_input(
            "Select Report Date",
            value=date.today(),
            max_value=date.today()
        )
    with col2:
        st.markdown("###")  # Spacing
        if st.button("📅 View Today's Report"):
            report_date = date.today()
            st.rerun()

    try:
        # Fetch data
        current_data, previous_data = fetch_daily_data(report_date)
        weekly_data = fetch_weekly_trend(report_date)

        if current_data.empty:
            st.info("👀 No data available for the selected date. Try selecting a different date.")
            return

        # Display metrics
        st.markdown("---")
        display_metrics_cards(current_data, previous_data)

        # Display charts
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_profit_chart(current_data), use_container_width=True)

        with col2:
            if not weekly_data.empty:
                st.plotly_chart(create_weekly_trend_chart(weekly_data), use_container_width=True)
            else:
                st.info("No weekly trend data available.")

        # Detailed data table
        st.markdown("---")
        with st.expander("📋 View Detailed Data"):
            st.dataframe(
                current_data.style.format({
                    'profit': '฿{:,.2f}'
                }),
                use_container_width=True
            )

            csv = current_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Report",
                csv,
                f"profit_report_{report_date}.csv",
                "text/csv",
                key='download-csv'
            )

    except Exception as e:
        st.error(f"❌ Error generating report: {str(e)}")
        st.info("Please try again or contact support if the problem persists.")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Financial Reports",
        page_icon="📊",
        layout="wide"
    )
    reports()