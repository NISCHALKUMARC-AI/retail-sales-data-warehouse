
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "database" / "sales_warehouse.db"
SQL_FILE = BASE_DIR / "src" / "analytics.sql"

conn = sqlite3.connect(DB_FILE)

with open(SQL_FILE, "r", encoding="utf-8") as file:
    sql_content = file.read()

queries = [
    query.strip()
    for query in sql_content.split(";")
    if query.strip()
]

for i, query in enumerate(queries, start=1):
    print(f"\n{'=' * 50}")
    print(f"QUERY {i} RESULTS")
    print("=" * 50)

    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))

conn.close()
print("\nSQL ANALYTICS COMPLETED!")
