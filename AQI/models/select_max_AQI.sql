select max(aqius) as max FROM {{ source('AQI','pollution_data')}}