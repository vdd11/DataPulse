import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

def generate_sales_data(n_orders=5000):
    Path("data").mkdir(exist_ok=True)

    categories = ["Technology", "Furniture", "Office Supplies"]
    regions = ["Northeast", "South", "Midwest", "West"]
    segments = ["Consumer", "Corporate", "Small Business"]

    products = {
        "Technology": ["Laptop", "Monitor", "Keyboard", "Mouse", "Printer"],
        "Furniture": ["Desk", "Chair", "Bookshelf", "Table", "Cabinet"],
        "Office Supplies": ["Paper", "Pens", "Folders", "Binders", "Stapler"]
    }

    dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")

    rows = []

    for i in range(1, n_orders + 1):
        category = np.random.choice(categories)
        product = np.random.choice(products[category])
        region = np.random.choice(regions)
        segment = np.random.choice(segments)
        order_date = np.random.choice(dates)

        quantity = np.random.randint(1, 8)

        base_price = {
            "Laptop": 950,
            "Monitor": 250,
            "Keyboard": 60,
            "Mouse": 35,
            "Printer": 180,
            "Desk": 350,
            "Chair": 220,
            "Bookshelf": 160,
            "Table": 280,
            "Cabinet": 190,
            "Paper": 20,
            "Pens": 12,
            "Folders": 15,
            "Binders": 18,
            "Stapler": 10
        }[product]

        discount = np.random.choice([0, 0.05, 0.10, 0.15, 0.20], p=[0.45, 0.2, 0.15, 0.12, 0.08])
        sales = quantity * base_price * (1 - discount)

        cost_rate = np.random.uniform(0.55, 0.82)
        cost = sales * cost_rate
        profit = sales - cost

        customer_id = f"CUST_{np.random.randint(1, 801):04d}"

        rows.append({
            "order_id": f"ORD_{i:05d}",
            "order_date": order_date,
            "customer_id": customer_id,
            "region": region,
            "segment": segment,
            "category": category,
            "product": product,
            "quantity": quantity,
            "discount": round(discount, 2),
            "sales": round(sales, 2),
            "cost": round(cost, 2),
            "profit": round(profit, 2)
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("order_date")

    df.to_csv("data/sales_data.csv", index=False)
    print("Generated data/sales_data.csv")

if __name__ == "__main__":
    generate_sales_data()
