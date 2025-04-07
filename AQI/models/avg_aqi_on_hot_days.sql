SELECT AVG(p.aqius) AS avg_aqi_hot_days
FROM  {{ source('AQI','pollution_data')}} p
JOIN {{ source('AQI','weather_data')}} w ON p.timestamp = w.timestamp
WHERE w.temperature > 35
/* ค่า AQI เฉลี่ยของวันที่อุณหภูมิสูงกว่า 35°C */