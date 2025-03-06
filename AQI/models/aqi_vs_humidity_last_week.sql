SELECT p.timestamp, p.aqius, w.humidity
FROM {{ source('AQI','pollution_data')}} p
JOIN {{ source('AQI','weather_data')}} w ON p.timestamp = w.timestamp
WHERE p.timestamp >= NOW() - INTERVAL '7 days'
ORDER BY p.timestamp