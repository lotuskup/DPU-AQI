WITH weekly_data AS (
    SELECT DATE_TRUNC('week', timestamp) AS week, AVG(aqius) AS avg_aqi_us
    FROM {{ source('AQI','pollution_data')}}
    GROUP BY week
)
SELECT 
    week,
    avg_aqi_us,
    LAG(avg_aqi_us) OVER (ORDER BY week) AS prev_week_avg_aqi,
    avg_aqi_us - LAG(avg_aqi_us) OVER (ORDER BY week) AS change_from_last_week
FROM weekly_data
ORDER BY week DESC
LIMIT 2
