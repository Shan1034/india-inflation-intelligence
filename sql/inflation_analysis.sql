
USE india_inflation_intelligence;

-- 1. Verify total records
SELECT COUNT(*) AS total_records
FROM category_inflation;

-- 2. Count records by month
SELECT month, COUNT(*) AS records
FROM category_inflation
GROUP BY month;

-- 3. Top 5 increases in inflation
SELECT
    j.group_name,
    j.combined_inflation AS July_inflation,
    a.combined_inflation AS August_inflation,
    a.combined_inflation - j.combined_inflation AS change_pp
FROM category_inflation j
JOIN category_inflation a
    ON j.group_code = a.group_code
WHERE j.month = 'July-2026'
  AND a.month = 'August-2026'
ORDER BY change_pp DESC
LIMIT 5;

-- 4. Top 5 decreases in inflation
SELECT
    j.group_name,
    j.combined_inflation AS July_inflation,
    a.combined_inflation AS August_inflation,
    a.combined_inflation - j.combined_inflation AS change_pp
FROM category_inflation j
JOIN category_inflation a
    ON j.group_code = a.group_code
WHERE j.month = 'July-2026'
  AND a.month = 'August-2026'
ORDER BY change_pp ASC
LIMIT 5;


-- 5. Compare rural and urban inflation in August 2026
SELECT
    group_name,
    rural_inflation,
    urban_inflation,
    rural_inflation - urban_inflation AS rural_urban_gap
FROM category_inflation
WHERE month = 'August-2026'
ORDER BY ABS(rural_inflation - urban_inflation) DESC
LIMIT 10;


-- 6. Compare average category inflation by month
SELECT
    month,
    ROUND(AVG(combined_inflation), 2) AS average_category_inflation
FROM category_inflation
GROUP BY month
ORDER BY month;