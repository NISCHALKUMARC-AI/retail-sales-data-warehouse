import pandas as pd
from pathlib import Path

# Load dataset
project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "Sample - Superstore.csv"

df = pd.read_csv(file_path, encoding="latin1")

# Dataset overview
print("\n--- DATASET OVERVIEW ---")
print("Shape:", df.shape)

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- FIRST 5 RECORDS ---")
print(df.head())

print("\n--- DATA TYPES ---")
print(df.info())

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())

print("\n--- STATISTICAL SUMMARY ---")
print(df.describe())

print("\n--- BUSINESS OVERVIEW ---")
print("Total Sales:", df["Sales"].sum())
print("Total Profit:", df["Profit"].sum())
print("Total Quantity:", df["Quantity"].sum())
print("Unique Customers:", df["Customer ID"].nunique())
print("Unique Products:", df["Product ID"].nunique())
print("Unique Orders:", df["Order ID"].nunique())

print("\n--- SALES BY CATEGORY ---")
print(df.groupby("Category")["Sales"].sum().sort_values(ascending=False))

print("\n--- SALES BY REGION ---")
print(df.groupby("Region")["Sales"].sum().sort_values(ascending=False))