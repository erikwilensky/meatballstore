import streamlit as st
import pandas as pd  # Add this import
from db.database import get_connection

def date_range_input(label_start, label_end):
    """
    Helper for date range selection.
    """
    start_date = st.date_input(label_start, value=pd.Timestamp.today().date())
    end_date = st.date_input(label_end, value=pd.Timestamp.today().date())
    return start_date, end_date


def multiselect_input(options):
    """
    Helper for multiselect input.
    """
    return st.multiselect("Select series to display:", options, default=options)


def transform_to_dataframe(data):
    """
    Transform raw query data to a DataFrame.
    """
    return pd.DataFrame(data, columns=["Date", "Metric", "Value"]).pivot(index="Date", columns="Metric", values="Value").reset_index()


def add_profit_column(df):
    """
    Add profit column to the DataFrame.
    """
    df["Profit"] = df.get("Sales", 0) / 2 - df.get("Salad Cost", 0) - 200


def plot_chart(df, selected_series):
    """
    Plot line chart for the selected series.
    """
    if selected_series:
        chart_data = df[["Date"] + selected_series].set_index("Date")
        st.line_chart(chart_data, use_container_width=True)
    else:
        st.warning("No series selected. Please select at least one series to display.")


def display_detailed_data(df):
    """
    Display detailed data table.
    """
    st.write("### Detailed Data")
    st.dataframe(df, use_container_width=True)


def generate_usage_report():
    """
    Main page for generating usage reports for all shops.
    """
    st.subheader("Reports")
    report_type = st.radio("Select a report type:", ["Barber Shop", "Shoe Shop", "Meatball Shop"], horizontal=True)

    if report_type == "Barber Shop":
        barber_shop_reports()
    elif report_type == "Shoe Shop":
        shoe_shop_reports()
    elif report_type == "Meatball Shop":
        meatball_shop_reports()


def barber_shop_reports():
    """
    Generate reports for the Barber Shop with dynamic series selection.
    """
    st.subheader("Barber Shop Reports")
    st.info("Select a date range and series to view haircut and revenue trends.")

    # Initialize session state for date range and series selection
    if "barber_start_date" not in st.session_state:
        st.session_state.barber_start_date = pd.Timestamp.today().date()
    if "barber_end_date" not in st.session_state:
        st.session_state.barber_end_date = pd.Timestamp.today().date()
    if "barber_selected_series" not in st.session_state:
        st.session_state.barber_selected_series = ["Adult Haircuts", "Child Haircuts", "Free Haircuts", "Revenue", "Profit"]

    # Date range selection
    start_date = st.date_input("Start Date", value=st.session_state.barber_start_date)
    end_date = st.date_input("End Date", value=st.session_state.barber_end_date)

    # Update session state if dates are modified
    if start_date != st.session_state.barber_start_date:
        st.session_state.barber_start_date = start_date
    if end_date != st.session_state.barber_end_date:
        st.session_state.barber_end_date = end_date

    # Multiselect for dynamic series selection
    available_series = ["Adult Haircuts", "Child Haircuts", "Free Haircuts", "Revenue", "Profit"]
    selected_series = st.multiselect(
        "Select series to display:",
        options=available_series,
        default=st.session_state.barber_selected_series
    )

    # Update session state if series are modified
    if selected_series != st.session_state.barber_selected_series:
        st.session_state.barber_selected_series = selected_series

    # Generate report button
    if st.button("Generate Report"):
        # Fetch and process data
        with get_connection() as conn:
            query = """
                SELECT date, metric, value
                FROM daily_entries
                WHERE shop = 'Barber Shop' AND date BETWEEN ? AND ?
            """
            data = conn.execute(query, (st.session_state.barber_start_date, st.session_state.barber_end_date)).fetchall()

        if not data:
            st.warning("No data found for the selected date range.")
            return

        # Transform data into a DataFrame
        df = pd.DataFrame(data, columns=["Date", "Metric", "Value"])
        df = df.pivot(index="Date", columns="Metric", values="Value").reset_index()
        df["Revenue"] = (df.get("Adult Haircuts", 0) * 120 + df.get("Child Haircuts", 0) * 100) / 2
        df["Profit"] = df["Revenue"] - 260

        if st.session_state.barber_selected_series:
            # Filter DataFrame to include only selected series
            chart_data = df[["Date"] + st.session_state.barber_selected_series].set_index("Date")
            st.line_chart(chart_data, use_container_width=True)
        else:
            st.warning("No series selected. Please select at least one series to display.")

        # Display detailed data
        st.write("### Detailed Data")
        st.dataframe(df, use_container_width=True)




def shoe_shop_reports():
    """
    Generate reports for the Shoe Shop.
    """
    st.subheader("Shoe Shop Reports")
    st.info("Select a date range to view revenue trends.")

    # Date range selection
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Generate Report"):
        with get_connection() as conn:
            query = """
                SELECT date, value
                FROM daily_entries
                WHERE shop = 'Shoe Shop' AND metric = 'Revenue' AND date BETWEEN ? AND ?
            """
            data = conn.execute(query, (start_date, end_date)).fetchall()

        if not data:
            st.warning("No data found for the selected date range.")
            return

        # Transform data into a DataFrame
        df = pd.DataFrame(data, columns=["Date", "Revenue"])
        st.line_chart(df.set_index("Date"), use_container_width=True)
        st.write("### Detailed Data")
        st.dataframe(df, use_container_width=True)


def meatball_shop_reports():
    """
    Generate reports for the Meatball Shop with dynamic series selection.
    """
    st.subheader("Meatball Shop Reports")
    report_type = st.radio(
        "Select Report Type",
        ["Daily Trends", "Weekly/Monthly Sales", "Profit vs. Inventory Cost"],
        horizontal=True
    )

    if report_type == "Daily Trends":
        generate_daily_trends_report()
    elif report_type == "Weekly/Monthly Sales":
        generate_sales_report()
    elif report_type == "Profit vs. Inventory Cost":
        generate_profit_vs_inventory_report()


def generate_daily_trends_report():
    """
    Generate daily trends report for the Meatball Shop.
    """
    st.info("Select a date range and series to view daily sales and profit trends.")
    start_date, end_date = date_range_input("Start Date", "End Date")
    selected_series = multiselect_input(["Sales", "Salad Cost", "Profit"])

    if st.button("Generate Daily Report"):
        with get_connection() as conn:
            query = """
                SELECT date, metric, value
                FROM daily_entries
                WHERE shop = 'Meatball Stand' AND date BETWEEN ? AND ?
            """
            data = conn.execute(query, (start_date, end_date)).fetchall()

        if not data:
            st.warning("No data found for the selected date range.")
            return

        df = transform_to_dataframe(data)
        add_profit_column(df)
        plot_chart(df, selected_series)
        display_detailed_data(df)


def generate_sales_report():
    """
    Generate weekly or monthly sales report for the Meatball Shop.
    """
    st.info("Select a period to view total sales of each product.")
    time_period = st.selectbox("Time Period", ["Weekly", "Monthly"])

    if st.button("Generate Sales Report"):
        with get_connection() as conn:
            query = """
                SELECT strftime('%Y-%W', date) AS week, metric, SUM(value) AS total
                FROM daily_entries
                WHERE shop = 'Meatball Stand' AND metric = 'Sales'
                GROUP BY week, metric
            """ if time_period == "Weekly" else """
                SELECT strftime('%Y-%m', date) AS month, metric, SUM(value) AS total
                FROM daily_entries
                WHERE shop = 'Meatball Stand' AND metric = 'Sales'
                GROUP BY month, metric
            """
            data = conn.execute(query).fetchall()

        if not data:
            st.warning("No data found for the selected time period.")
            return

        df = pd.DataFrame(data, columns=["Period", "Metric", "Total Sales"])
        st.bar_chart(df.set_index("Period")["Total Sales"], use_container_width=True)
        st.dataframe(df, use_container_width=True)


def generate_profit_vs_inventory_report():
    """
    Compare weekly profit and revenue with inventory cost.
    """
    st.info("Compare weekly profit and revenue with inventory cost.")
    if st.button("Generate Profit vs. Inventory Report"):
        with get_connection() as conn:
            # Fetch inventory data
            query = """
                SELECT CAST(wi.week_number AS TEXT) AS week, wi.year, SUM(wi.quantity * ii.cost) AS inventory_cost
                FROM weekly_inventory wi
                JOIN inventory_items ii ON wi.item_id = ii.id
                WHERE wi.inventory_type = 'start'
                GROUP BY wi.week_number, wi.year
            """
            inventory_data = conn.execute(query).fetchall()

            # Fetch profit data
            profit_query = """
                SELECT strftime('%Y-%W', date) AS week, 
                       SUM(CASE WHEN metric = 'Sales' THEN value ELSE 0 END) / 2 - 
                       SUM(CASE WHEN metric = 'Salad Cost' THEN value ELSE 0 END) - 
                       200 AS profit,
                       SUM(CASE WHEN metric = 'Sales' THEN value ELSE 0 END) AS revenue
                FROM daily_entries
                WHERE shop = 'Meatball Stand'
                GROUP BY week
            """
            profit_data = conn.execute(profit_query).fetchall()

        # Handle no data case
        if not inventory_data or not profit_data:
            st.warning("No data found for the selected time period.")
            return

        # Convert data to DataFrames
        inventory_df = pd.DataFrame(inventory_data, columns=["Week", "Year", "Inventory Cost"])
        profit_df = pd.DataFrame(profit_data, columns=["Week", "Profit", "Revenue"])

        # Convert Week columns to string for both DataFrames
        inventory_df["Week"] = inventory_df["Week"].astype(str)
        profit_df["Week"] = profit_df["Week"].astype(str)

        # Merge the two DataFrames on Week
        report_df = pd.merge(inventory_df, profit_df, on="Week", how="outer").fillna(0)

        # Plot the report
        st.line_chart(report_df.set_index("Week")[["Profit", "Revenue", "Inventory Cost"]], use_container_width=True)

        # Display detailed report
        st.write("### Detailed Report")
        st.dataframe(report_df, use_container_width=True)



