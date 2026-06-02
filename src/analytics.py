import sqlite3
import pandas as pd

DB_PATH = "database/datapulse.db"

def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_sales_data():
    return run_query("SELECT * FROM sales")

def get_kpis():
    query = """
    SELECT
        SUM(sales) AS total_revenue,
        SUM(profit) AS total_profit,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(profit) * 1.0 / SUM(sales) AS profit_margin
    FROM sales;
    """
    return run_query(query)

def monthly_revenue():
    query = """
    SELECT
        substr(order_date, 1, 7) AS month,
        SUM(sales) AS revenue,
        SUM(profit) AS profit
    FROM sales
    GROUP BY month
    ORDER BY month;
    """
    return run_query(query)

def revenue_by_category():
    query = """
    SELECT
        category,
        SUM(sales) AS revenue,
        SUM(profit) AS profit
    FROM sales
    GROUP BY category
    ORDER BY revenue DESC;
    """
    return run_query(query)

def revenue_by_region():
    query = """
    SELECT
        region,
        SUM(sales) AS revenue,
        SUM(profit) AS profit
    FROM sales
    GROUP BY region
    ORDER BY revenue DESC;
    """
    return run_query(query)

def top_products():
    query = """
    SELECT
        product,
        category,
        SUM(quantity) AS units_sold,
        SUM(sales) AS revenue,
        SUM(profit) AS profit
    FROM sales
    GROUP BY product, category
    ORDER BY revenue DESC
    LIMIT 10;
    """
    return run_query(query)

def top_customers():
    query = """
    SELECT
        customer_id,
        COUNT(order_id) AS orders,
        SUM(sales) AS revenue,
        SUM(profit) AS profit
    FROM sales
    GROUP BY customer_id
    ORDER BY revenue DESC
    LIMIT 20;
    """
    return run_query(query)

def customer_segments():
    query = """
    SELECT
        segment,
        COUNT(DISTINCT customer_id) AS customers,
        SUM(sales) AS revenue,
        SUM(profit) AS profit
    FROM sales
    GROUP BY segment
    ORDER BY revenue DESC;
    """
    return run_query(query)
