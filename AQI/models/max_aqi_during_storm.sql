SELECT MAX(p.aqius) AS max_aqi_during_storm
FROM  {{ source('AQI','pollution_data')}} p
JOIN {{ source('AQI','weather_data')}} w ON p.timestamp = w.timestamp
WHERE w.wind_speed > 20

/* ค่า AQI สูงสุดในช่วงที่มีพายุ */