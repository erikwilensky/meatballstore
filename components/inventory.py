import streamlit as st
from db.database import get_connection

def display_meatball_inventory():
    """
    Manage Meatball Inventory: Separate views for managing items, setting weekly inventory, and viewing reports.
    """
    st.subheader("Meatball Inventory Management")
    menu = st.radio(
        "Select an Option",
        ["Manage Items", "Set Weekly Inventory", "View Reports"],
        horizontal=True
    )

    if menu == "Manage Items":
        manage_inventory_items()
    elif menu == "Set Weekly Inventory":
        set_inventory()
    elif menu == "View Reports":
        view_completed_weeks()


def manage_inventory_items():
    """
    Manage inventory items with options to add, view, and edit items.
    """
    st.write("### Manage Inventory Items")

    with st.expander("Add New Item"):
        item_name = st.text_input("Item Name", key="new_item_name")
        item_cost = st.number_input("Cost (฿)", min_value=0, step=1, key="new_item_cost")
        if st.button("Add Item"):
            if item_name:
                with get_connection() as conn:
                    try:
                        conn.execute("""
                            INSERT INTO inventory_items (name, cost)
                            VALUES (?, ?)
                            ON CONFLICT(name) DO UPDATE SET cost = excluded.cost
                        """, (item_name, item_cost))
                        conn.commit()
                        st.success(f"Item '{item_name}' added/updated successfully!")
                    except Exception as e:
                        st.error(f"Error adding item: {str(e)}")
            else:
                st.warning("Item name cannot be empty.")

    with st.expander("View and Edit Items"):
        with get_connection() as conn:
            items = conn.execute("SELECT id, name, cost FROM inventory_items").fetchall()

        if items:
            item_options = {f"{item['name']} (฿{item['cost']})": item for item in items}
            selected_item = st.selectbox("Select an Item to Edit", list(item_options.keys()), key="edit_item")
            if selected_item:
                item = item_options[selected_item]
                new_name = st.text_input("Edit Name", value=item["name"], key="edit_item_name")
                new_cost = st.number_input("Edit Cost (฿)", value=item["cost"], min_value=0, step=1, key="edit_item_cost")

                if st.button("Save Changes"):
                    with get_connection() as conn:
                        try:
                            conn.execute("""
                                UPDATE inventory_items
                                SET name = ?, cost = ?
                                WHERE id = ?
                            """, (new_name, new_cost, item["id"]))
                            conn.commit()
                            st.success(f"Item '{item['name']}' updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating item: {str(e)}")
        else:
            st.warning("No items found. Add items first.")


def set_inventory():
    """
    Allow users to set start or end weekly inventory for all items.
    """
    st.write("### Add or Update Weekly Inventory")
    inventory_type_label = st.radio("Inventory Type", ["Start of the Week (Monday)", "End of the Week (Sunday)"], horizontal=True)
    inventory_type = "start" if inventory_type_label.startswith("Start") else "end"
    allowed_days = ["Monday"] if inventory_type == "start" else ["Sunday"]

    record_date = st.date_input(f"Select a {allowed_days[0]}:", help="Choose a date that matches the selected inventory type.")
    if record_date.strftime("%A") not in allowed_days:
        st.warning(f"Please select a {allowed_days[0]}.")
        return

    with get_connection() as conn:
        items = conn.execute("SELECT id, name FROM inventory_items").fetchall()

    if not items:
        st.warning("No inventory items found. Please add items first.")
        return

    with st.form("weekly_inventory_form"):
        st.write(f"### {inventory_type_label} Inventory for Week {record_date.isocalendar()[1]}, {record_date.year}")
        quantities = {}
        for item in items:
            item_id = item["id"]
            item_name = item["name"]
            quantities[item_id] = st.number_input(f"{item_name} Quantity", min_value=0.0, step=0.1, key=f"item_{item_id}")

        submitted = st.form_submit_button("Save Inventory")
        if submitted:
            week_number = record_date.isocalendar()[1]
            year = record_date.year

            with get_connection() as conn:
                try:
                    for item_id, quantity in quantities.items():
                        conn.execute("""
                            INSERT INTO weekly_inventory (item_id, inventory_type, quantity, record_date, week_number, year)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ON CONFLICT (item_id, inventory_type, week_number, year)
                            DO UPDATE SET quantity = excluded.quantity, record_date = excluded.record_date
                        """, (item_id, inventory_type, quantity, record_date, week_number, year))

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
                    st.success(f"{inventory_type_label} inventory saved successfully for Week {week_number}, {year}!")
                except Exception as e:
                    st.error(f"Error saving inventory: {str(e)}")


def view_completed_weeks():
    """
    Display completed weeks and allow the user to view inventory usage reports.
    """
    st.write("### Completed Weeks")
    with get_connection() as conn:
        weekly_tracking = conn.execute("""
            SELECT week_number, year, start_inventory, end_inventory
            FROM weekly_tracking
            ORDER BY year, week_number
        """).fetchall()

    if not weekly_tracking:
        st.info("No weekly inventory data available.")
    else:
        for record in weekly_tracking:
            week_number = record["week_number"]
            year = record["year"]
            start_inventory = record["start_inventory"]
            end_inventory = record["end_inventory"]

            if start_inventory and end_inventory:
                button_label = f"✅ Week {week_number}, {year}"
                if st.button(button_label, key=f"week_{week_number}_{year}"):
                    generate_inventory_usage_report(week_number, year)
            else:
                st.write(f"❌ Week {week_number}, {year} - Incomplete")


def generate_inventory_usage_report(week_number, year):
    """
    Generate and display a usage report for a specific week.
    """
    st.subheader(f"Usage Report for Week {week_number}, {year}")

    with get_connection() as conn:
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

        if not start_inventory or not end_inventory:
            st.warning("Incomplete inventory records for this week.")
            return

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

        st.table(usage_report)
        st.write(f"**Total Cost for Week {week_number}, {year}: ฿{int(total_cost)}**")
