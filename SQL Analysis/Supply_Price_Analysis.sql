-- To  check the price increase YoY growth --
WITH avg_price AS 
(
SELECT 
	commodity,
    pricetype,
    unit,
    YEAR(STR_TO_DATE(date, '%d/%m/%Y')) AS Years,
    ROUND(AVG(price), 2) AS current_year_price
FROM supply_price
GROUP BY commodity,
		 YEAR(STR_TO_DATE(date, '%d/%m/%Y')),
         pricetype,
         unit
),

window_function AS 
(
SELECT 
	ap.*,
    LAG(current_year_price) 
    OVER(
		PARTITION BY commodity
        ORDER BY Years
	) AS previous_year
FROM avg_price ap
),

calculation AS 
(
SELECT 
	wf.*,
    ROUND(current_year_price - previous_year, 2)AS price_Increase
FROM window_function wf
)

SELECT 
	commodity,
    Years,
    current_year_price,
    previous_year,
    price_Increase,
    
    ROUND(price_Increase / previous_year * 100, 2)  AS price_increase_Percentage
FROM calculation
WHERE pricetype = 'Retail'
  AND unit = 'KG'
;
--         -----------------------------------------------------------------------------------------
-- Minimum and maximum observed price per commodityWITH prices AS 
WITH prices AS 
(
    SELECT 
        commodity,
        MIN(price) AS minimum_price,
        MAX(price) AS maximum_price
    FROM supply_price
    GROUP BY commodity
)

SELECT 
    commodity,
    minimum_price,
    maximum_price,
    
    ROUND(maximum_price - minimum_price, 2) AS price_range

FROM prices;

-- ------------------------------------------------------------------------------------------------------------------------------
-- Wholesale vs Retail Price Difference
WITH computation AS 
(
SELECT
    commodity,
    
    MAX(CASE
        WHEN pricetype = 'Wholesale' THEN price
    END) AS wholesale_price,

    MAX(CASE
        WHEN pricetype = 'Retail' THEN price
    END) AS retail_price

FROM supply_price
GROUP BY commodity
)

SELECT 
	commodity,
    wholesale_price,
    retail_price,
    
   ROUND(retail_price - wholesale_price, 2) AS Difference
    
FROM computation;

 -- -- - - - - - - - - -----------------------------------------------------------------------------------------------------------------------------
-- Regions has commodity prices that are higher or lower than the overall Philippines average? ---------------------------------------------------
WITH commodity_avg AS
(
SELECT 
	admin1,
    commodity,
    AVG(price) AS avg_Price
FROM supply_price
GROUP BY admin1,
		commodity
),

philippine_avg AS 
(
SELECT 
	ca.*,
    AVG(avg_Price)
    OVER (
		PARTITION BY commodity
	) AS avg_Phil
FROM commodity_avg ca

),

differences AS 
(
SELECT 
	pa.*,
     avg_price - avg_Phil AS difference
FROM philippine_avg pa
),

percentages AS 
(
SELECT 
	df.*,
	 ROUND(difference / avg_Phil * 100, 2)  AS percentage
FROM differences df
)

SELECT 
	admin1,
    commodity,
    avg_Price,    
    avg_Phil,
    difference,
    percentage,
    
    CASE 
		WHEN avg_Phil > avg_Price THEN 'Lower'
        ELSE 'Higher' 
	END AS Status
    
FROM percentages;
-- --------------------------------------------------------------------------------------------------------------------------------
-- Price Volatility 
WITH vola AS 
(
SELECT 
	commodity,
    ROUND(AVG(price),2) AS avg_Price,
    round(STDDEV(price),2)AS volatility
FROM supply_price
GROUP BY commodity
)

SELECT 
    commodity,
    avg_Price,
    volatility
FROM vola
ORDER BY volatility DESC;
-- -----------------------------------------------------------------------------------------------------------------------------------------
-- Latest Price vs Previous Price
WITH daily_prices AS
(
    SELECT
        commodity,
        date,
        AVG(price) AS avg_price
    FROM supply_price
    GROUP BY commodity, date
),

ranked_prices AS
(
    SELECT
        commodity,
        date,
        ROUND(avg_price, 2) AS avg_price,

        ROW_NUMBER() OVER (
            PARTITION BY commodity
            ORDER BY STR_TO_DATE(date, '%d/%m/%Y') DESC
        ) AS rn,

        LAG(avg_price) OVER (
            PARTITION BY commodity
            ORDER BY STR_TO_DATE(date, '%d/%m/%Y') ASC
        ) AS previous_price

    FROM daily_prices
),

latest_prices AS
(
    SELECT
        commodity,
        date,
        avg_price AS latest_price,
        previous_price
    FROM ranked_prices
    WHERE rn = 1
)

SELECT
    commodity,
    date,
    latest_price,
    ROUND(previous_price, 2) AS previous_price,

    ROUND(
        latest_price - previous_price,
        2
    ) AS price_change,

    ROUND(
        (latest_price - previous_price) / previous_price * 100,
        2
    ) AS percentage_change

FROM latest_prices;


