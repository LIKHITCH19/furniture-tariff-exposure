-- Effective duty rate by month, all furniture and wood vs non-wood.
-- rate = calculated duty / customs value entered for consumption

WITH by_segment AS (
    SELECT
        month,
        CASE WHEN is_wood THEN 'Wood furniture' ELSE 'Non-wood furniture' END AS segment,
        SUM(general_imports_usd)     AS imports_usd,
        SUM(consumption_imports_usd) AS consumption_usd,
        SUM(calculated_duty_usd)     AS duty_usd
    FROM imports
    GROUP BY 1, 2
),

all_furniture AS (
    SELECT
        month,
        'All furniture' AS segment,
        SUM(imports_usd)     AS imports_usd,
        SUM(consumption_usd) AS consumption_usd,
        SUM(duty_usd)        AS duty_usd
    FROM by_segment
    GROUP BY 1
),

combined AS (
    SELECT * FROM by_segment
    UNION ALL
    SELECT * FROM all_furniture
)

SELECT
    c.month,
    p.phase,
    c.segment,
    c.imports_usd,
    c.consumption_usd,
    c.duty_usd,
    c.duty_usd / NULLIF(c.consumption_usd, 0) AS effective_rate
FROM combined c
LEFT JOIN policy_phases p
    ON c.month BETWEEN p.start_month AND COALESCE(p.end_month, DATE '9999-12-31')
ORDER BY c.month, c.segment;
