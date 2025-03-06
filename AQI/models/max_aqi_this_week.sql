SELECT MAX(aqius) AS max_aqi_us
FROM {{ source('AQI','pollution_data')}}
WHERE timestamp >= NOW() - INTERVAL '7 days'
