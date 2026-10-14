-- Effective rate by supplier x product line over the last 3 months.
-- Used by the Excel model. Cells with under $2M of goods are left blank.

WITH bounds AS (
    SELECT MAX(month) AS latest FROM imports
),

last_3m AS (
    SELECT i.*
    FROM imports i, bounds b
    WHERE i.month > b.latest - INTERVAL 3 MONTH
),

major AS (
    SELECT country
    FROM last_3m
    GROUP BY country
    ORDER BY SUM(general_imports_usd) DESC
    LIMIT 12
)

SELECT
    w.hs6,
    ANY_VALUE(w.hs_label)            AS hs_label,
    w.country,
    MIN(w.month)                     AS window_start,
    MAX(w.month)                     AS window_end,
    SUM(w.consumption_imports_usd)   AS consumption_usd,
    SUM(w.calculated_duty_usd)       AS duty_usd,
    CASE
        WHEN SUM(w.consumption_imports_usd) >= 2e6
        THEN SUM(w.calculated_duty_usd) / SUM(w.consumption_imports_usd)
    END                              AS effective_rate
FROM last_3m w
JOIN major USING (country)
GROUP BY w.hs6, w.country
ORDER BY w.hs6, consumption_usd DESC;
