-- Effective duty rate for the 12 biggest suppliers in each policy phase.
-- Weighted by dollars (total duty / total value), not an average of monthly rates.

WITH major AS (
    SELECT country
    FROM imports
    GROUP BY country
    ORDER BY SUM(general_imports_usd) DESC
    LIMIT 12
)

SELECT
    p.phase_id,
    p.phase,
    i.country,
    COUNT(DISTINCT i.month)        AS months,
    SUM(i.consumption_imports_usd) AS consumption_usd,
    SUM(i.calculated_duty_usd)     AS duty_usd,
    SUM(i.calculated_duty_usd)
        / NULLIF(SUM(i.consumption_imports_usd), 0) AS effective_rate,
    SUM(i.calculated_duty_usd) FILTER (WHERE i.is_wood)
        / NULLIF(SUM(i.consumption_imports_usd) FILTER (WHERE i.is_wood), 0) AS wood_rate,
    SUM(i.calculated_duty_usd) FILTER (WHERE NOT i.is_wood)
        / NULLIF(SUM(i.consumption_imports_usd) FILTER (WHERE NOT i.is_wood), 0) AS non_wood_rate
FROM imports i
JOIN major USING (country)
JOIN policy_phases p
    ON i.month BETWEEN p.start_month AND COALESCE(p.end_month, DATE '9999-12-31')
GROUP BY 1, 2, 3
ORDER BY p.phase_id, consumption_usd DESC;
