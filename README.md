# Retail Sales Data Warehouse & Business Analytics

## Project Overview
This project builds a Retail Sales Data Warehouse using Python, SQL, and SQLite. It transforms raw retail sales data into a structured star-schema warehouse and provides an interactive business analytics dashboard using Streamlit.

## Technologies Used
- Python
- Pandas and NumPy
- SQL
- SQLite
- Streamlit
- Matplotlib and Plotly

## Project Features
- Exploratory Data Analysis (EDA)
- Data cleaning and preprocessing
- ETL pipeline
- Star-schema data warehouse
- SQL-based business analytics
- Interactive Streamlit dashboard
- Sales, profit, customer, product and regional analysis

## Project Structure
```text
retail_sales_data_warehouse/
├── data/
├── database/
├── src/
├── dashboard/
├── requirements.txt
└── README.md
```

## How to Run

1. Install the required packages:
   `pip install -r requirements.txt`

2. Run the ETL script:
   `python src/etl.py`

3. Create the data warehouse:
   `python src/warehouse.py`

4. Run SQL analytics:
   `python src/run_analytics.py`

5. Launch the dashboard:
   `python -m streamlit run dashboard/app.py`

## Objective
To demonstrate practical skills in data analysis, data engineering, SQL, data warehousing and business intelligence.