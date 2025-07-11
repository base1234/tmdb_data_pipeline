WITH enriched AS (
    SELECT
        m.genre_id,
        g.genre_name,
        m.vote_average
    FROM {{ ref('staging_movies') }} m
    LEFT JOIN {{ ref('genre_lookup') }} g
      ON m.genre_id = g.genre_id
    WHERE m.vote_average IS NOT NULL
)

SELECT
    genre_name,
    COUNT(*) AS movie_count,
    ROUND(AVG(vote_average), 2) AS avg_rating
FROM enriched
GROUP BY genre_name
ORDER BY avg_rating DESC, movie_count DESC
LIMIT 10
