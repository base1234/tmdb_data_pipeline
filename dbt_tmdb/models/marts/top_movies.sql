-- This analytics model surfaces the top-rated movies (score ≥ 8).
-- It can be used in dashboards or joined with metadata tables.

WITH top_movies_raw AS (
    SELECT
        m.title,
        m.genre_id,
        g.genre_name,
        m.vote_average,
        m.release_date
    FROM {{ ref('staging_movies') }} m
    LEFT JOIN {{ ref('genre_lookup') }} g
      ON m.genre_id = g.genre_id
    WHERE m.vote_average >= 8
),

top_movies_with_year AS (
    SELECT
        *,
        EXTRACT(YEAR FROM CAST(release_date AS DATE)) AS release_year
    FROM top_movies_raw
)

SELECT 
    title,
    genre_name,
    vote_average,
    release_date,
    release_year
FROM top_movies_with_year
ORDER BY vote_average DESC, release_date DESC
LIMIT 20
