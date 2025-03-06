SELECT DATE_TRUNC('month', timestamp) AS month, 
       MAX(aqius) AS max_aqi_us, 
       MIN(aqius) AS min_aqi_us
FROM {{ source('AQI','pollution_data')}}
WHERE timestamp >= DATE_TRUNC('year', NOW())
GROUP BY month
ORDER BY month
