
-- 1. Total sales, profit and quantity
SELECT
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    SUM(Quantity) AS Total_Quantity
FROM Fact_Sales;


-- 2. Sales by product category
SELECT
    p.Category,
    ROUND(SUM(f.Sales), 2) AS Total_Sales
FROM Fact_Sales f
JOIN Dim_Product p
    ON f.Product_Key = p.Product_Key
GROUP BY p.Category
ORDER BY Total_Sales DESC;


-- 3. Profit by region
SELECT
    r.Region,
    ROUND(SUM(f.Profit), 2) AS Total_Profit
FROM Fact_Sales f
JOIN Dim_Region r
    ON f.Region_Key = r.Region_Key
GROUP BY r.Region
ORDER BY Total_Profit DESC;


-- 4. Top 10 customers by sales
SELECT
    c.Customer_Name,
    ROUND(SUM(f.Sales), 2) AS Total_Sales
FROM Fact_Sales f
JOIN Dim_Customer c
    ON f.Customer_Key = c.Customer_Key
GROUP BY c.Customer_Name
ORDER BY Total_Sales DESC
LIMIT 10;


-- 5. Monthly sales analysis
SELECT
    d.Year,
    d.Month,
    d.Month_Name,
    ROUND(SUM(f.Sales), 2) AS Monthly_Sales
FROM Fact_Sales f
JOIN Dim_Date d
    ON f.Date_Key = d.Date_Key
GROUP BY d.Year, d.Month, d.Month_Name
ORDER BY d.Year, d.Month;


-- 6. Top 10 products by profit
SELECT
    p.Product_Name,
    ROUND(SUM(f.Profit), 2) AS Total_Profit
FROM Fact_Sales f
JOIN Dim_Product p
    ON f.Product_Key = p.Product_Key
GROUP BY p.Product_ID, p.Product_Name
ORDER BY Total_Profit DESC
LIMIT 10;
