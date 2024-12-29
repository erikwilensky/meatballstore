import streamlit as st
from db.database import get_connection


def generate_usage_report():
    """
    Display a grid of completed weeks with clickable green check buttons for generating usage reports.
    """
    st.header("Inventory Usage Reports")
    st.info("Click on a completed week (✅) to view the inventory usage report.")

    with get_connection() as conn:
        # Fetch all weekly tracking records
        weekly_tracking = conn.execute("""
            SELECT week_number, year, start_inventory, end_inventory
            FROM weekly_tracking
            ORDER BY year, week_number
        """).fetchall()

    # Display completed and incomplete weeks
    st.subheader("Completed Weeks")
    for record in weekly_tracking:
        week_number = record["week_number"]
        year = record["year"]
        start_inventory = record["start_inventory"]
        end_inventory = record["end_inventory"]

        if start_inventory and end_inventory:
            # Create a button for completed weeks
            button_label = f"✅ Week {week_number}, {year}"
            if st.button(button_label, key=f"week_{week_number}_{year}"):
                view_weekly_report(week_number, year)
                return  # Stop rendering further buttons once a report is displayed
        else:
            # Display incomplete weeks without a button
            st.write(f"❌ Week {week_number}, {year} - Incomplete")


def view_weekly_report(week_number, year):
    """
    Generate and display a usage report for a specific week.
    """
    st.subheader(f"Usage Report for Week {week_number}, {year}")

    with get_connection() as conn:
        # Fetch start and end inventory for the selected week
        start_inventory = conn.execute("""
            SELECT ii.name, ii.cost, wi.quantity
            FROM weekly_inventory wi
            JOIN inventory_items ii ON wi.item_id = ii.id
            WHERE wi.inventory_type = 'start' AND wi.week_number = ? AND wi.year = ?
        """, (week_number, year)).fetchall()

        end_inventory = conn.execute("""
            SELECT ii.name, ii.cost, wi.quantity
            FROM weekly_inventory wi
            JOIN inventory_items ii ON wi.item_id = ii.id
            WHERE wi.inventory_type = 'end' AND wi.week_number = ? AND wi.year = ?
        """, (week_number, year)).fetchall()

        # Ensure both start and end inventories exist
        if not start_inventory or not end_inventory:
            st.warning("Incomplete inventory records for this week.")
            return

        # Calculate usage and costs
        usage_report = []
        total_cost = 0
        for start_item in start_inventory:
            for end_item in end_inventory:
                if start_item["name"] == end_item["name"]:
                    amount_used = start_item["quantity"] - end_item["quantity"]
                    cost = int(amount_used * start_item["cost"])  # Ensure integer values for cost
                    usage_report.append({
                        "Name": start_item["name"],
                        "Amount Used": round(amount_used, 1),  # One decimal for quantity
                        "Unit Cost": int(start_item["cost"]),
                        "Total Cost": int(cost)
                    })
                    total_cost += cost

        # Display the report
        st.table(usage_report)
        st.write(f"**Total Cost for Week {week_number}, {year}: ฿{int(total_cost)}**")
