
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Retail Sales BI Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #183153;
}
h2, h3 {
    color: #24476b;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "database" / "sales_warehouse.db"

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_FILE)

    query = """
    SELECT
        f.Order_ID,
        f.Sales,
        f.Profit,
        f.Quantity,
        f.Discount,
        c.Customer_Name,
        p.Product_Name,
        p.Category,
        p.Sub_Category,
        d.Year,
        d.Month,
        d.Month_Name,
        r.Region,
        r.State
    FROM Fact_Sales f
    JOIN Dim_Customer c
        ON f.Customer_Key = c.Customer_Key
    JOIN Dim_Product p
        ON f.Product_Key = p.Product_Key
    JOIN Dim_Date d
        ON f.Date_Key = d.Date_Key
    JOIN Dim_Region r
        ON f.Region_Key = r.Region_Key
    """

    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

df = load_data()

# ---------------- TITLE ----------------

st.title("📊 Retail Sales & Business Intelligence")
st.caption(
    "An interactive analytics dashboard built using "
    "Python, SQL, SQLite, Pandas, Plotly and Streamlit."
)

st.divider()

# ---------------- FILTERS ----------------

st.sidebar.title("Dashboard Filters")

categories = st.sidebar.multiselect(
    "Product Category",
    sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

regions = st.sidebar.multiselect(
    "Region",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

years = st.sidebar.multiselect(
    "Order Year",
    sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)

filtered_df = df[
    df["Category"].isin(categories)
    & df["Region"].isin(regions)
    & df["Year"].isin(years)
]

if filtered_df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# ---------------- KPI METRICS ----------------

st.subheader("Business Performance")

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_orders = filtered_df["Order_ID"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Units Sold", f"{total_quantity:,}")
col4.metric("Total Orders", f"{total_orders:,}")

st.divider()

# ---------------- CATEGORY & REGION ----------------

st.subheader("Sales and Regional Performance")

col1, col2 = st.columns(2)

with col1:
    category_data = (
        filtered_df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig = px.bar(
        category_data,
        x="Category",
        y="Sales",
        color="Category",
        title="Sales by Product Category",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    region_data = (
        filtered_df.groupby("Region", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=False)
    )

    fig = px.bar(
        region_data,
        x="Region",
        y="Profit",
        color="Region",
        title="Profit by Region",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- MONTHLY TRENDS ----------------

st.subheader("Monthly Sales and Profit Trends")

monthly = (
    filtered_df.groupby(["Year", "Month"], as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    .sort_values(["Year", "Month"])
)

monthly["Period"] = (
    monthly["Year"].astype(str)
    + "-"
    + monthly["Month"].astype(str).str.zfill(2)
)

fig = px.line(
    monthly,
    x="Period",
    y=["Sales", "Profit"],
    markers=True,
    title="Monthly Sales vs Profit"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- PRODUCT PERFORMANCE ----------------

st.subheader("Product Performance")

product_data = (
    filtered_df.groupby("Product_Name", as_index=False)
    .agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum")
    )
)

col1, col2 = st.columns(2)

with col1:
    top_products = product_data.nlargest(10, "Total_Sales")

    fig = px.bar(
        top_products.sort_values("Total_Sales"),
        x="Total_Sales",
        y="Product_Name",
        orientation="h",
        title="Top 10 Products by Sales"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    bottom_products = product_data.nsmallest(10, "Total_Profit")

    fig = px.bar(
        bottom_products.sort_values("Total_Profit"),
        x="Total_Profit",
        y="Product_Name",
        orientation="h",
        title="10 Products with Lowest Profit"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- DISCOUNT ANALYSIS ----------------

st.subheader("Discount Analysis")

discount_data = (
    filtered_df.groupby("Discount", as_index=False)
    .agg(
        Average_Profit=("Profit", "mean"),
        Total_Sales=("Sales", "sum")
    )
    .sort_values("Discount")
)

fig = px.bar(
    discount_data,
    x="Discount",
    y="Average_Profit",
    title="Average Profit at Different Discount Levels",
    labels={"Average_Profit": "Average Profit"}
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- TOP CUSTOMERS ----------------

st.subheader("Top 10 Customers")

customer_data = (
    filtered_df.groupby("Customer_Name", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
    .head(10)
)

st.dataframe(customer_data, use_container_width=True)

# ---------------- DOWNLOAD REPORT ----------------

st.subheader("Download Business Report")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Sales Report",
    data=csv_data,
    file_name="retail_sales_report.csv",
    mime="text/csv"
)

st.divider()

st.caption("Retail Sales Data Warehouse | Business Analytics Project")
