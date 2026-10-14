-- Exposure by product line: last 12 months vs calendar 2024.
-- extra_duty = duty paid minus what the same goods would have paid at the
-- line's 2024 rate.

WITH bounds AS (
    SELECT MAX(month) AS latest FROM imports
),

ttm AS (
    SELECT i.*
    FROM imports i, bounds b
    WHERE i.month > b.latest - INTERVAL 12 MONTH
),

recent AS (
    SELECT
        hs6,
        ANY_VALUE(hs_label)            AS hs_label,
        BOOL_OR(is_wood)               AS is_wood,
        SUM(general_imports_usd)       AS ttm_imports_usd,
        SUM(consumption_imports_usd)   AS ttm_consumption_usd,
        SUM(calculated_duty_usd)       AS ttm_duty_usd,
        SUM(calculated_duty_usd) / NULLIF(SUM(consumption_imports_usd), 0) AS ttm_rate,
        SUM(general_imports_usd) FILTER (WHERE country = 'China')
            / NULLIF(SUM(general_imports_usd), 0) AS ttm_china_share,
        SUM(general_imports_usd) FILTER (WHERE country = 'Vietnam')
            / NULLIF(SUM(general_imports_usd), 0) AS ttm_vietnam_share
    FROM ttm
    GROUP BY 1
),

baseline AS (
    SELECT
        hs6,
        SUM(general_imports_usd)       AS base_imports_usd,
        SUM(calculated_duty_usd) / NULLIF(SUM(consumption_imports_usd), 0) AS base_rate,
        SUM(general_imports_usd) FILTER (WHERE country = 'China')
            / NULLIF(SUM(general_imports_usd), 0) AS base_china_share
    FROM imports
    WHERE year = 2024
    GROUP BY 1
)

SELECT
    r.hs6,
    r.hs_label,
    r.is_wood,
    r.ttm_imports_usd,
    b.base_imports_usd,
    r.ttm_imports_usd / NULLIF(b.base_imports_usd, 0) - 1    AS import_change_pct,
    b.base_rate,
    r.ttm_rate,
    (r.ttm_rate - b.base_rate) * 100                          AS rate_change_pts,
    r.ttm_duty_usd,
    r.ttm_duty_usd - b.base_rate * r.ttm_consumption_usd      AS extra_duty_usd,
    b.base_china_share,
    r.ttm_china_share,
    r.ttm_vietnam_share
FROM recent r
JOIN baseline b USING (hs6)
ORDER BY extra_duty_usd DESC;
