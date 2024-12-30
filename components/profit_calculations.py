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
