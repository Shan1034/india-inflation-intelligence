
import pandas as pd
import mysql.connector
from pathlib import Path

csv_path = Path("data/processed/group_inflation_july_august_2026.csv")
df = pd.read_csv(csv_path)

df["serial_no"] = pd.to_numeric(
    df["serial_no"].astype(str).str.strip().str.rstrip("."),
    errors="raise"
).astype(int)

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=input("Enter your MySQL root password: "),
    database="india_inflation_intelligence"
)

cursor = connection.cursor()

sql = """
INSERT INTO category_inflation (
    serial_no, group_code, group_name,
    rural_index, urban_index, combined_index,
    rural_inflation, urban_inflation, combined_inflation, month
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

columns = [
    "serial_no", "group_code", "group_name",
    "rural_index", "urban_index", "combined_index",
    "rural_inflation", "urban_inflation",
    "combined_inflation", "month"
]

records = df[columns].where(pd.notna(df[columns]), None)
cursor.execute("TRUNCATE TABLE category_inflation")
cursor.executemany(sql, list(records.itertuples(index=False, name=None)))
connection.commit()

print("Rows imported:", cursor.rowcount)

cursor.close()
connection.close()
