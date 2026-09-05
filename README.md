# Philippines Food Price Analytics

## 📌 Project Overview

An end-to-end data analytics project analyzing food prices in the Philippines using **Python, pandas, SQL, and Power BI**.

The project uses Philippine food price data from the **World Food Programme (WFP) Price Database** to demonstrate an end-to-end analytics workflow — from automated data extraction and transformation to SQL-based business analysis and interactive Power BI visualization.

## 🎯 Business Objective

The objective of this project is to analyze Philippine food price patterns and provide insights into:

* Food price trends over time
* Price differences between wholesale and retail markets
* Regional price differences
* Commodity price changes
* Price increases and decreases
* Price volatility
* Recent price movements

## 🛠️ Tools & Technologies

* **Python**
* **pandas**
* **SQL / MySQL**
* **Power BI**
* **DAX**
* **Git & GitHub**

## 🔄 Project Workflow

```text
Raw WFP Food Price Data
        ↓
Python / pandas ETL
        ↓
Data Cleaning & Transformation
        ↓
SQL Business Analysis
        ↓
Power BI Dashboard
        ↓
Business Insights
```

## 🐍 Python ETL

Python and pandas were used to automate the data preparation process.

The ETL pipeline handles tasks such as:

* Extracting food price data from CSV files
* Cleaning and transforming the dataset
* Standardizing data formats
* Performing data-quality checks
* Preparing the dataset for analysis
* Generating processed output for downstream analysis

## 🗄️ SQL Analysis

SQL was used to answer business-oriented analytical questions, including:

* Year-over-year commodity price changes
* Minimum and maximum observed prices
* Wholesale vs. retail price differences
* Regional price premiums
* Price volatility
* Latest price vs. previous price
* Commodity price increases between selected years

The analysis uses **CTEs, conditional aggregation, window functions, date functions, and calculated metrics** to transform raw data into business insights.

## 📊 Power BI Dashboard

Power BI was used to create an interactive dashboard focused on Philippine food price trends and comparisons.

### Key KPIs

* Average Price
* Latest Price
* YoY Growth %
* Price Volatility

### Key Visualizations

* Price Trend Over Time
* Average Price by Region
* Commodity Price Ranking
* Wholesale vs. Retail Price Comparison

Interactive filters allow users to explore the data by commodity, region, price type, and date.

## 💡 Key Skills Demonstrated

This project demonstrates my ability to:

* Build an automated ETL workflow using Python and pandas
* Perform data-quality checks and transformations
* Write SQL queries for real-world business questions
* Analyze trends and price differences
* Use window functions for analytical calculations
* Build interactive Power BI dashboards
* Translate raw data into meaningful business insights
* Combine multiple tools into an end-to-end analytics workflow

## 📁 Project Structure

```text
philippines-food-price-analytics/
│
├── data/
│   └── raw/
│
├── python/
│   └── ETL_Automation.py

│
├── sql/
│   └── business_analysis.sql
│
├── powerbi/
│   └── food_price_dashboard.pbix
│
├── output/
│   └── cleaned_food_prices.csv
│
├── screenshots/
│   └── dashboard.png
│
└── README.md
```

## 📚 Data Source

The dataset is based on the **World Food Programme (WFP) Price Database** and contains food price information from markets across the Philippines.

Source: Kaggle — Philippines Food Prices Dataset.

## 👤 Project Purpose

This project was developed as part of my **Data Analyst portfolio** to demonstrate practical experience in data preparation, SQL analysis, automation, and business intelligence using a real-world dataset.
