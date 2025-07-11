-- Calculates the average vote and total movie count by release year.
-- Useful for understanding rating trends over time.

WITH valid_movies AS (
    SELECT
        release_date,
        vote_average
    FROM {{ ref('staging_movies') }}
    WHERE release_date IS NOT NULL
      AND release_date != ''
      AND vote_average IS NOT NULL
),

movies_by_year AS (
    SELECT
        EXTRACT(YEAR FROM CAST(release_date AS DATE)) AS release_year,
        vote_average
    FROM valid_movies
)

SELECT
    release_year,
    COUNT(*) AS movie_count,
    ROUND(AVG(vote_average), 2) AS avg_vote
FROM movies_by_year
GROUP BY release_year
ORDER BY release_year DESC

