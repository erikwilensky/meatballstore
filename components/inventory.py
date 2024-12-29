import streamlit as st
from db.database import get_connection

def set_weekly_inventory():
    """
    Manage inventory items and weekly inventory, and generate usage reports.
    """
    st.subheader("Meatball Inventory Management")

    # Tabs for different functionalities
    tab = st.radio(
        "Select an option",
        ["Manage Inventory Items", "Set Weekly Inventory"],
        horizontal=True
    )

    if tab == "Manage Inventory Items":
        manage_inventory_items()
    elif tab == "Set Weekly Inventory":
        set_inventory_and_reports()


def manage_inventory_items():
    """
    Add, edit, or view inventory items.
    """
    st.write("### Manage Inventory Items")

    # Form to add inventory items
    with st.form("add_item_form"):
        item_name = st.text_input("Item Name")
        unit_cost = st.number_input("Unit Cost (฿)", min_value=0, step=1)

        add_item_button = st.form_submit_button("Add Item")
        if add_item_button:
            with get_connection() as conn:
                try:
                    conn.execute("""
                        INSERT INTO inventory_items (name, cost)
                        VALUES (?, ?)
                        ON CONFLICT (name)
                        DO UPDATE SET cost = excluded.cost
                    """, (item_name, unit_cost))
                    conn.commit()
                    st.success(f"Item '{item_name}' added/updated successfully!")
                except Exception as e:
                    st.error(f"Error adding/updating item: {str(e)}")

    # Display existing inventory items
    st.write("### Existing Inventory Items")
    with get_connection() as conn:
        items = conn.execute("SELECT * FROM inventory_items").fetchall()

    if items:
        st.table([{"Name": item["name"], "Unit Cost": item["cost"]} for item in items])
    else:
        st.info("No inventory items found. Please add some items.")


def set_inventory_and_reports():
    """
    Record start/end inventory and generate usage reports.
    """
    st.write("### Set Weekly Inventory")

    # Inventory entry form
    with st.form("weekly_inventory_form"):
        item_id = st.number_input("Item ID", min_value=1, step=1)
        inventory_type = st.selectbox("Inventory Type", ["start", "end"])
        quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
        record_date = st.date_input("Record Date")
        week_number = record_date.isocalendar()[1]
        year = record_date.year

        submitted = st.form_submit_button("Save Inventory")
        if submitted:
            with get_connection() as conn:
                try:
                    conn.execute("""
                        INSERT INTO weekly_inventory (item_id, inventory_type, quantity, record_date, week_number, year)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT (item_id, inventory_type, week_number, year)
                        DO UPDATE SET quantity = excluded.quantity, record_date = excluded.record_date
                    """, (item_id, inventory_type, quantity, record_date, week_number, year))

                    # Update weekly tracking table
                    if inventory_type == "start":
                        conn.execute("""
                            INSERT OR IGNORE INTO weekly_tracking (week_number, year, start_inventory)
                            VALUES (?, ?, 1)
                            ON CONFLICT (week_number, year)
                            DO UPDATE SET start_inventory = 1
                        """, (week_number, year))
                    elif inventory_type == "end":
                        conn.execute("""
                            INSERT OR IGNORE INTO weekly_tracking (week_number, year, end_inventory)
                            VALUES (?, ?, 1)
                            ON CONFLICT (week_number, year)
                            DO UPDATE SET end_inventory = 1
                        """, (week_number, year))

                    conn.commit()
                    st.success("Inventory saved successfully!")
                except Exception as e:
                    st.error(f"Error saving inventory: {str(e)}")

    # Divider for the reports section
    st.write("---")

    # Display completed weeks and generate reports
    st.write("### Completed Weeks")
    with get_connection() as conn:
        weekly_tracking = conn.execute("""
            SELECT week_number, year, start_inventory, end_inventory
            FROM weekly_tracking
            ORDER BY year, week_number
        """).fetchall()

    for record in weekly_tracking:
        week_number = record["week_number"]
        year = record["year"]
        start_inventory = record["start_inventory"]
        end_inventory = record["end_inventory"]

        if start_inventory and end_inventory:
            # Completed week
            button_label = f"✅ Week {week_number}, {year}"
            if st.button(button_label, key=f"week_{week_number}_{year}"):
                generate_inventory_usage_report(week_number, year)
                return  # Stop further rendering after generating a report
        else:
            # Incomplete week
            st.write(f"❌ Week {week_number}, {year} - Incomplete")


def generate_inventory_usage_report(week_number, year):
    """
    Generate and display a usage report for a specific week.
    """
    st.subheader(f"Usage Report for Week {week_number}, {year}")

    with get_connection() as conn:
        # Fetch start inventory
        start_inventory = conn.execute("""
            SELECT ii.name, ii.cost, wi.quantity
            FROM weekly_inventory wi
            JOIN inventory_items ii ON wi.item_id = ii.id
            WHERE wi.inventory_type = 'start' AND wi.week_number = ? AND wi.year = ?
        """, (week_number, year)).fetchall()

        # Fetch end inventory
        end_inventory = conn.execute("""
            SELECT ii.name, ii.cost, wi.quantity
            FROM weekly_inventory wi
            JOIN inventory_items ii ON wi.item_id = ii.id
            WHERE wi.inventory_type = 'end' AND wi.week_number = ? AND wi.year = ?
        """, (week_number, year)).fetchall()

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
                    cost = int(amount_used * start_item["cost"])
                    usage_report.append({
                        "Name": start_item["name"],
                        "Amount Used": round(amount_used, 1),
                        "Unit Cost": int(start_item["cost"]),
                        "Total Cost": int(cost)
                    })
                    total_cost += cost

        # Display the report
        st.table(usage_report)
        st.write(f"**Total Cost for Week {week_number}, {year}: ฿{int(total_cost)}**")
