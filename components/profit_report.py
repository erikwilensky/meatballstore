import streamlit as st
from components.profit_chart import generate_profit_pie_chart, generate_profit_line_chart
from db.database import get_connection
import datetime

def display_profit_report():
    """
    Generate and display a profit report based on a date range.
    """
    st.subheader("Profit Report")

    # Date range input
    today = datetime.date.today()
    start_date, end_date = st.date_input(
        "Select Date Range:",
        value=(today, today),
        key="profit_report_dates"
    )

    # Validate date range
    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
        return

    # Chart type selector for multi-day ranges
    chart_type = None
    if start_date != end_date:
        chart_type = st.radio("Select Chart Type:", ["Pie Chart", "Line Chart"], horizontal=True)
    else:
        st.write("Single-day range: Displaying only a pie chart.")

    # Generate report button
    if st.button("Generate Report"):
        # Fetch data from database
        with get_connection() as conn:
            barber_data = conn.execute("""
                SELECT date, metric, value FROM daily_entries
                WHERE shop = 'Barber Shop' AND date BETWEEN ? AND ?
            """, (start_date, end_date)).fetchall()

            shoe_data = conn.execute("""
                SELECT date, value FROM daily_entries
                WHERE shop = 'Shoe Shop' AND metric = 'Revenue' AND date BETWEEN ? AND ?
            """, (start_date, end_date)).fetchall()

            meatball_data = conn.execute("""
                SELECT date, metric, value FROM daily_entries
                WHERE shop = 'Meatball Stand' AND date BETWEEN ? AND ?
            """, (start_date, end_date)).fetchall()

        # Calculate profits
        barber_profit = calculate_barber_profit(barber_data)
        shoe_profit = calculate_shoe_profit(shoe_data)
        meatball_profit = calculate_meatball_profit(meatball_data)

        # Display total profits
        st.write(f"Barber Shop Profit: ฿{barber_profit}")
        st.write(f"Shoe Shop Profit: ฿{shoe_profit}")
        st.write(f"Meatball Stand Profit: ฿{meatball_profit}")

        total_profit = barber_profit + shoe_profit + meatball_profit
        st.write(f"**Total Profit: ฿{total_profit}**")

        # Chart rendering
        if start_date == end_date:
            generate_profit_pie_chart(barber_profit, shoe_profit, meatball_profit)
        else:
            if chart_type == "Pie Chart":
                generate_profit_pie_chart(barber_profit, shoe_profit, meatball_profit)
            elif chart_type == "Line Chart":
                line_data = prepare_line_chart_data(barber_data, shoe_data, meatball_data)
                generate_profit_line_chart(line_data, start_date, end_date)

def calculate_barber_profit(data):
    """
    Calculate profit for the Barber Shop.
    """
    adult_price = 120
    child_price = 80
    free_price = 0

    adult_haircuts = sum(row["value"] for row in data if row["metric"] == "Adult Haircuts")
    child_haircuts = sum(row["value"] for row in data if row["metric"] == "Child Haircuts")
    free_haircuts = sum(row["value"] for row in data if row["metric"] == "Free Haircuts")

    revenue = (adult_haircuts * adult_price) + (child_haircuts * child_price) + (free_haircuts * free_price)
    cost = 260
    return revenue // 2 - cost

def calculate_shoe_profit(data):
    """
    Calculate profit for the Shoe Shop.
    """
    revenue = sum(row["value"] for row in data)
    cost = 110
    return revenue - cost

def calculate_meatball_profit(data):
    """
    Calculate profit for the Meatball Stand.
    """
    sales = sum(row["value"] for row in data if row["metric"] == "Sales")
    salad_cost = sum(row["value"] for row in data if row["metric"] == "Salad Cost")
    return sales // 2 - salad_cost - 200

def prepare_line_chart_data(barber_data, shoe_data, meatball_data):
    """
    Prepare data for the line chart.
    """
    line_data = {
        "Barber Shop": {},
        "Shoe Shop": {},
        "Meatball Stand": {}
    }

    for row in barber_data:
        date = row["date"]
        profit = calculate_barber_profit([row])
        if date in line_data["Barber Shop"]:
            line_data["Barber Shop"][date] += profit
        else:
            line_data["Barber Shop"][date] = profit

    for row in shoe_data:
        date = row["date"]
        profit = calculate_shoe_profit([row])
        if date in line_data["Shoe Shop"]:
            line_data["Shoe Shop"][date] += profit
        else:
            line_data["Shoe Shop"][date] = profit

    for row in meatball_data:
        date = row["date"]
        profit = calculate_meatball_profit([row])
        if date in line_data["Meatball Stand"]:
            line_data["Meatball Stand"][date] += profit
        else:
            line_data["Meatball Stand"][date] = profit

    return line_data
