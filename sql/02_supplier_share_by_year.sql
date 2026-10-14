-- Share of US furniture imports by supplier and year.
-- Anyone who was top 10 in any year gets their own row, the rest go to 'All other'.
-- 2026 is a partial year (see months_covered) so compare shares, not totals.

WITH yearly AS (
    SELECT
        year,
        country,
        SUM(general_imports_usd) AS imports_usd
    FROM imports
    GROUP BY 1, 2
),

ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY year ORDER BY imports_usd DESC) AS rank_in_year
    FROM yearly
),

top_suppliers AS (
    SELECT DISTINCT country
    FROM ranked
    WHERE rank_in_year <= 10
),

months AS (
    SELECT year, COUNT(DISTINCT month) AS months_covered
    FROM imports
    GROUP BY 1
)

SELECT
    y.year,
    m.months_covered,
    CASE WHEN t.country IS NOT NULL THEN y.country ELSE 'All other' END AS supplier,
    SUM(y.imports_usd) AS imports_usd,
    SUM(y.imports_usd) / SUM(SUM(y.imports_usd)) OVER (PARTITION BY y.year) AS share
FROM yearly y
LEFT JOIN top_suppliers t ON y.country = t.country
JOIN months m ON y.year = m.year
GROUP BY 1, 2, 3
ORDER BY y.year, imports_usd DESC;
