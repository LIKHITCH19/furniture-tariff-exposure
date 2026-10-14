-- BLS furniture import prices (pre-duty) vs the same prices with duty added,
-- both indexed to Jan 2025 = 100 (last month before the first 2025 tariff).
-- If suppliers had absorbed the tariff, pre_duty_index would have dropped.
-- Note: the BLS series is "furniture, household goods", broader than HS 94.

WITH duty AS (
    SELECT
        month,
        SUM(calculated_duty_usd) / NULLIF(SUM(consumption_imports_usd), 0) AS effective_rate
    FROM imports
    GROUP BY 1
),

prices AS (
    SELECT
        CAST(month AS DATE) AS month,
        MAX(index_value) FILTER (WHERE series_id = 'EIUIR41000') AS furniture_idx,
        MAX(index_value) FILTER (WHERE series_id = 'EIUIR')      AS all_imports_idx
    FROM bls_prices
    GROUP BY 1
),

base AS (
    SELECT p.furniture_idx AS f0, p.all_imports_idx AS a0, d.effective_rate AS r0
    FROM prices p
    JOIN duty d USING (month)
    WHERE p.month = DATE '2025-01-01'
)

SELECT
    d.month,
    d.effective_rate,
    p.furniture_idx,
    p.all_imports_idx,
    100 * p.furniture_idx / b.f0                                   AS pre_duty_index,
    100 * p.furniture_idx / b.f0 * (1 + d.effective_rate) / (1 + b.r0) AS with_duty_index,
    100 * p.all_imports_idx / b.a0                                 AS all_imports_index
FROM duty d
LEFT JOIN prices p USING (month)
CROSS JOIN base b
ORDER BY d.month;
