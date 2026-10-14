-- Who gained and lost share between 2024 and the latest year.
-- Same months in each year (Jan through the latest month) since 2026 is partial.

WITH bounds AS (
    SELECT MAX(month) AS latest FROM imports
),

ytd AS (
    SELECT
        i.year,
        i.country,
        SUM(i.general_imports_usd) AS imports_usd
    FROM imports i, bounds b
    WHERE month(i.month) <= month(b.latest)
      AND i.year BETWEEN year(b.latest) - 2 AND year(b.latest)
    GROUP BY 1, 2
),

wide AS (
    SELECT
        y.country,
        SUM(imports_usd) FILTER (WHERE year = year(b.latest) - 2) AS ytd_base,
        SUM(imports_usd) FILTER (WHERE year = year(b.latest) - 1) AS ytd_prior,
        SUM(imports_usd) FILTER (WHERE year = year(b.latest))     AS ytd_latest
    FROM ytd y, bounds b
    GROUP BY 1
),

totals AS (
    SELECT SUM(ytd_base) AS t_base, SUM(ytd_prior) AS t_prior, SUM(ytd_latest) AS t_latest
    FROM wide
)

SELECT
    'Jan-' || strftime(b.latest, '%b') || ', '
        || (year(b.latest) - 2) || ' vs ' || year(b.latest)        AS period_compared,
    w.country,
    COALESCE(w.ytd_base, 0)   AS ytd_base_usd,
    COALESCE(w.ytd_prior, 0)  AS ytd_prior_usd,
    COALESCE(w.ytd_latest, 0) AS ytd_latest_usd,
    COALESCE(w.ytd_base, 0)   / t.t_base   AS share_base,
    COALESCE(w.ytd_latest, 0) / t.t_latest AS share_latest,
    (COALESCE(w.ytd_latest, 0) / t.t_latest
        - COALESCE(w.ytd_base, 0) / t.t_base) * 100                AS share_change_pts,
    COALESCE(w.ytd_latest, 0) - COALESCE(w.ytd_base, 0)            AS value_change_usd,
    COALESCE(w.ytd_latest, 0) / NULLIF(w.ytd_base, 0) - 1          AS value_change_pct
FROM wide w, totals t, bounds b
-- skip small suppliers (under $50M in both years)
WHERE GREATEST(COALESCE(w.ytd_base, 0), COALESCE(w.ytd_latest, 0)) >= 50e6
ORDER BY share_change_pts DESC;
