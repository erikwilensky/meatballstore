def set_weekly_inventory():
    st.subheader("Set Weekly Inventory")

    # Period type selection
    inventory_type = st.radio("Inventory Type", ["Start of Week (Monday)", "End of Week (Sunday)"])
    inventory_type_db = "start" if inventory_type == "Start of Week (Monday)" else "end"

    # Date input for inventory
    inventory_date = st.date_input("Inventory Date", value=date.today())

    # Validate the selected date
    valid_start_date = inventory_date.weekday() == 0  # Monday
    valid_end_date = inventory_date.weekday() == 6  # Sunday

    if (inventory_type_db == "start" and not valid_start_date) or (inventory_type_db == "end" and not valid_end_date):
        st.error(f"The date must be a valid {inventory_type}!")
        return

    # Display inventory items
    st.subheader(f"Enter Inventory Levels for {inventory_type} ({inventory_date})")
    with get_connection() as conn:
        items = conn.execute("SELECT * FROM inventory_items").fetchall()

        for item in items:
            quantity = st.number_input(f"Quantity for {item['name']}", min_value=0.0, step=0.1)

            # Save button for each item
            if st.button(f"Save {item['name']} ({inventory_type})"):
                week_number = inventory_date.isocalendar()[1]
                year = inventory_date.year

                # Insert or update the inventory record
                conn.execute("""
                    INSERT INTO weekly_inventory (item_id, inventory_type, quantity, record_date, week_number, year)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(item_id, inventory_type, week_number, year) DO UPDATE SET
                        quantity = excluded.quantity
                """, (item["id"], inventory_type_db, quantity, inventory_date, week_number, year))

                # Update weekly tracking table
                tracking_column = "start_inventory" if inventory_type_db == "start" else "end_inventory"
                conn.execute(f"""
                    INSERT INTO weekly_tracking (week_number, year, {tracking_column})
                    VALUES (?, ?, 1)
                    ON CONFLICT(week_number, year) DO UPDATE SET
                        {tracking_column} = 1
                """, (week_number, year))

                conn.commit()
                st.success(f"Inventory for '{item['name']}' ({inventory_type}) saved successfully.")

    # Display reports
    st.subheader("Inventory Usage Reports")
    generate_inventory_report()


def generate_inventory_report():
    """
    Generate a report showing inventory usage, cost, and total expenses for a selected week.
    """
    st.info("Select a week to view the inventory usage report.")

    # Select week and year
    week_number = st.number_input("Enter Week Number", value=date.today().isocalendar()[1], min_value=1, max_value=52)
    year = st.number_input("Enter Year", value=date.today().year, min_value=2000, max_value=2100)

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
            st.warning("Incomplete inventory records for this week. Ensure both start and end inventories are entered.")
            return

        # Calculate usage and costs
        usage_report = []
        total_cost = 0
        for start_item in start_inventory:
            for end_item in end_inventory:
                if start_item["name"] == end_item["name"]:
                    amount_used = start_item["quantity"] - end_item["quantity"]
                    cost = amount_used * start_item["cost"]
                    usage_report.append({
                        "name": start_item["name"],
                        "amount_used": amount_used,
                        "unit_cost": start_item["cost"],
                        "total_cost": cost
                    })
                    total_cost += cost

        # Display the report
        st.table(usage_report)
        st.write(f"**Total Cost for Week {week_number}, {year}: ฿{total_cost}**")
