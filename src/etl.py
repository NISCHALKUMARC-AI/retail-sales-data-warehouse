
import pandas as pd
from pathlib import Path

# Project folder paths
project_folder = Path(__file__).resolve().parent.parent

input_file = project_folder / "data" / "Sample - Superstore.csv"
output_file = project_folder / "data" / "cleaned_sales.csv"

# =================================
# 1. EXTRACT
# =================================

print("Starting ETL Pipeline...")

df = pd.read_csv(input_file, encoding="latin1")

print("Original records:", len(df))

# =================================
# 2. TRANSFORM
# =================================

# Remove duplicate rows
df = df.drop_duplicates()

# Convert date columns
df["Order Date"] = pd.to_datetime(
    df["Order Date"], errors="coerce"
)

df["Ship Date"] = pd.to_datetime(
    df["Ship Date"], errors="coerce"
)

# Convert numeric columns
numeric_columns = [
    "Sales", "Profit", "Quantity", "Discount"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove records with missing important values
df = df.dropna(
    subset=[
        "Order ID", "Order Date", "Customer ID",
        "Product ID", "Sales", "Profit", "Quantity"
    ]
)

# Apply basic business rules
df = df[df["Quantity"] > 0]
df = df[df["Sales"] >= 0]

# Create additional date columns
df["Order Year"] = df["Order Date"].dt.year
df["Order Month"] = df["Order Date"].dt.month
df["Order Month Name"] = df["Order Date"].dt.month_name()

print("Cleaned records:", len(df))

# =================================
# 3. LOAD
# =================================

df.to_csv(output_file, index=False)

print("Cleaned dataset saved successfully!")
print("Final dataset shape:", df.shape)

print("ETL PIPELINE COMPLETED!")