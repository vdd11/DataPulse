import sqlite3
import pandas as pd
from pathlib import Path

Path("database").mkdir(exist_ok=True)

df = pd.read_csv("data/sales_data.csv")

conn = sqlite3.connect("database/datapulse.db")

df.to_sql("sales", conn, if_exists="replace", index=False)

conn.close()

print("SQLite database created at database/datapulse.db")
