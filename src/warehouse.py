
import pandas as pd
import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "cleaned_sales.csv"
DB_FILE = BASE_DIR / "database" / "sales_warehouse.db"

DB_FILE.parent.mkdir(parents=True, exist_ok=True)

print("Creating Star Schema Data Warehouse...")

# Load cleaned data
df = pd.read_csv(DATA_FILE)
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Connect to database
conn = sqlite3.connect(DB_FILE)
conn.execute("PRAGMA foreign_keys = ON")

# Create dimension tables
conn.executescript("""
DROP TABLE IF EXISTS Fact_Sales;
DROP TABLE IF EXISTS Dim_Customer;
DROP TABLE IF EXISTS Dim_Product;
DROP TABLE IF EXISTS Dim_Date;
DROP TABLE IF EXISTS Dim_Region;

CREATE TABLE Dim_Customer (
    Customer_Key INTEGER PRIMARY KEY,
    Customer_ID TEXT UNIQUE,
    Customer_Name TEXT,
    Segment TEXT
);

CREATE TABLE Dim_Product (
    Product_Key INTEGER PRIMARY KEY,
    Product_ID TEXT UNIQUE,
    Product_Name TEXT,
    Category TEXT,
    Sub_Category TEXT
);

CREATE TABLE Dim_Date (
    Date_Key INTEGER PRIMARY KEY,
    Full_Date TEXT UNIQUE,
    Year INTEGER,
    Month INTEGER,
    Month_Name TEXT,
    Quarter INTEGER
);

CREATE TABLE Dim_Region (
    Region_Key INTEGER PRIMARY KEY,
    Region TEXT,
    State TEXT,
    City TEXT,
    Postal_Code TEXT,
    UNIQUE (Region, State, City, Postal_Code)
);

CREATE TABLE Fact_Sales (
    Sales_Key INTEGER PRIMARY KEY,
    Order_ID TEXT,
    Customer_Key INTEGER,
    Product_Key INTEGER,
    Date_Key INTEGER,
    Region_Key INTEGER,
    Sales REAL,
    Quantity INTEGER,
    Profit REAL,
    Discount REAL,
    FOREIGN KEY (Customer_Key) REFERENCES Dim_Customer(Customer_Key),
    FOREIGN KEY (Product_Key) REFERENCES Dim_Product(Product_Key),
    FOREIGN KEY (Date_Key) REFERENCES Dim_Date(Date_Key),
    FOREIGN KEY (Region_Key) REFERENCES Dim_Region(Region_Key)
);
""")

# Populate customer dimension
customers = df[
    ["Customer ID", "Customer Name", "Segment"]
].drop_duplicates(subset=["Customer ID"]).reset_index(drop=True)

customers.insert(0, "Customer_Key", range(1, len(customers) + 1))
customers.columns = [
    "Customer_Key", "Customer_ID", "Customer_Name", "Segment"
]
customers.to_sql("Dim_Customer", conn, if_exists="append", index=False)

# Populate product dimension
products = df[
    ["Product ID", "Product Name", "Category", "Sub-Category"]
].drop_duplicates(subset=["Product ID"]).reset_index(drop=True)

products.insert(0, "Product_Key", range(1, len(products) + 1))
products.columns = [
    "Product_Key", "Product_ID", "Product_Name",
    "Category", "Sub_Category"
]
products.to_sql("Dim_Product", conn, if_exists="append", index=False)

# Populate date dimension
dates = pd.DataFrame({
    "Full_Date": df["Order Date"].dt.strftime("%Y-%m-%d").drop_duplicates()
}).reset_index(drop=True)

dates.insert(0, "Date_Key", range(1, len(dates) + 1))
date_values = pd.to_datetime(dates["Full_Date"])
dates["Year"] = date_values.dt.year
dates["Month"] = date_values.dt.month
dates["Month_Name"] = date_values.dt.month_name()
dates["Quarter"] = date_values.dt.quarter

dates.to_sql("Dim_Date", conn, if_exists="append", index=False)


# Populate region dimension
regions = df[
    ["Region", "State", "City", "Postal Code"]
].drop_duplicates().reset_index(drop=True)

# Clean postal code values before renaming
regions["Postal Code"] = regions["Postal Code"].astype("string").fillna("Unknown")

regions.insert(0, "Region_Key", range(1, len(regions) + 1))

regions.columns = [
    "Region_Key", "Region", "State", "City", "Postal_Code"
]

regions.to_sql("Dim_Region", conn, if_exists="append", index=False)

# Create region lookup dictionary
customer_map = dict(zip(customers["Customer_ID"], customers["Customer_Key"]))

product_map = dict(zip(products["Product_ID"], products["Product_Key"]))

date_map = dict(zip(dates["Full_Date"], dates["Date_Key"]))

region_columns = ["Region", "State", "City", "Postal_Code"]

region_map = {
    tuple(row): key
    for row, key in zip(
        regions[region_columns].itertuples(index=False, name=None),
        regions["Region_Key"]
    )
}

# Build fact table using dimension keys
fact = df.copy()
fact["Full_Date"] = fact["Order Date"].dt.strftime("%Y-%m-%d")

fact["Customer_Key"] = fact["Customer ID"].map(customer_map)
fact["Product_Key"] = fact["Product ID"].map(product_map)
fact["Date_Key"] = fact["Full_Date"].map(date_map)

fact["Postal Code"] = (
    fact["Postal Code"].astype("string").fillna("Unknown")
)

fact["Region_Key"] = [
    region_map[tuple(row)]
    for row in fact[
        ["Region", "State", "City", "Postal Code"]
    ].itertuples(index=False, name=None)
]

fact = fact[
    [
        "Order ID", "Customer_Key", "Product_Key",
        "Date_Key", "Region_Key", "Sales",
        "Quantity", "Profit", "Discount"
    ]
].copy()

fact.columns = [
    "Order_ID", "Customer_Key", "Product_Key",
    "Date_Key", "Region_Key", "Sales",
    "Quantity", "Profit", "Discount"
]

fact.to_sql("Fact_Sales", conn, if_exists="append", index=False)

# Validate warehouse
print("\nWAREHOUSE TABLE COUNTS:")

for table in [
    "Dim_Customer", "Dim_Product", "Dim_Date",
    "Dim_Region", "Fact_Sales"
]:
    count = pd.read_sql_query(
        f"SELECT COUNT(*) AS total FROM {table}", conn
    ).iloc[0, 0]
    print(f"{table}: {count} records")

foreign_key_errors = conn.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print("\nForeign key errors:", len(foreign_key_errors))
print("STAR SCHEMA DATA WAREHOUSE CREATED SUCCESSFULLY!")

conn.close()
