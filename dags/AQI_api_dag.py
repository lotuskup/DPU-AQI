import json
import os
from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils import timezone
from datetime import timedelta
import requests


DAG_FOLDER = "/opt/airflow/dags"

def _get_AQI_data():
    # API_KEY = os.environ.get("WEATHER_API_KEY")
    API_KEY = Variable.get("AQI_api_dag")
   
    url = "http://api.airvisual.com/v2/city?city=Sai Mai&state=Bangkok&country=Thailand&key="+API_KEY
    response = requests.get(url)
    print(response.url)

    data = response.json()
    print(data)

    with open(f"{DAG_FOLDER}/data.json", "w") as f:
        json.dump(data, f)


def _validate_data():
    with open(f"{DAG_FOLDER}/data.json", "r") as f:
        data = json.load(f)

        # ตรวจสอบว่า 'pollution' และ 'weather' มีข้อมูลหรือไม่
        assert data["data"]["current"].get("pollution") is not None, "Pollution data is missing"
        assert data["data"]["current"].get("weather") is not None, "Weather data is missing"

       

def _validate_AQI():
    with open(f"{DAG_FOLDER}/data.json", "r") as f:
        data = json.load(f)

        pollution_data = data["data"]["current"]["pollution"]
        weather = data["data"]["current"]["weather"]

        # ตรวจสอบค่าของ AQI US และ AQI CN ว่ามีค่าที่เหมาะสม
        aqius = pollution_data["aqius"]
        aqicn = pollution_data["aqicn"]
        
        assert 0 <= aqius <= 500, f"AQI US value out of range: {aqius}"
        assert 0 <= aqicn <= 500, f"AQI CN value out of range: {aqicn}"
       
        # ตรวจสอบค่าของอุณหภูมิ ความดัน ความชื้น และความเร็วลม
        tp = weather["tp"]  # อุณหภูมิ (°C)
        pr = weather["pr"]  # ความกดอากาศ (hPa)
        hu = weather["hu"]  # ความชื้น (%)
        ws = weather["ws"]  # ความเร็วลม (m/s)

        assert 0 <= tp <= 60, f"Temperature out of range: {tp}"
        assert 980 <= pr <= 1050, f"Pressure out of range: {pr}"
        assert 0 <= hu <= 100, f"Humidity out of range: {hu}"
        assert 0 <= ws <= 150, f"Wind speed out of range: {ws}"
       


def _create_pollution_data_table():
    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn",
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
   
    sql = """
        CREATE TABLE IF NOT EXISTS pollution_data (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        aqius INT NOT NULL,
        mainus VARCHAR(10) NOT NULL,
        aqicn INT NOT NULL,
        maincn VARCHAR(10) NOT NULL

        );
    """
    cursor.execute(sql)
    connection.commit()


def _create_weather_data_table():
    try:
        pg_hook = PostgresHook(
            postgres_conn_id="my_postgres_conn",
            schema="postgres"
        )
        connection = pg_hook.get_conn()
        cursor = connection.cursor()

        sql = """
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                temperature DECIMAL(5,2) NOT NULL,
                pressure INT NOT NULL,
                humidity INT NOT NULL,
                wind_speed DECIMAL(5,2) NOT NULL,
                wind_direction INT NOT NULL,
                icon VARCHAR(10) NOT NULL
            );
        """
        cursor.execute(sql)
        connection.commit()

    except Exception as e:
        print(f"Error creating table: {e}")
        connection.rollback()  # Rollback in case of error

    finally:
        cursor.close()  # Ensure cursor is closed
        connection.close()  # Ensure connection is closed


def _load_pollution_data_to_postgres():
    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn",
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    # โหลดข้อมูลจากไฟล์ JSON
    with open(os.path.join(DAG_FOLDER, "data.json"), "r") as f:
        data = json.load(f)

    # ดึงค่าที่ต้องการจาก JSON
   
    pollution = data["data"]["current"]["pollution"]
    timestamp = pollution["ts"]
    aqius = pollution["aqius"]
    mainus = pollution["mainus"]
    aqicn = pollution["aqicn"]
    maincn = pollution["maincn"]

    # ใช้ parameterized query เพื่อป้องกัน SQL Injection
    sql = """
        INSERT INTO pollution_data (timestamp, aqius, mainus, aqicn, maincn) 
        VALUES ( %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, ( timestamp, aqius, mainus, aqicn, maincn))
    connection.commit()
    cursor.close()
    connection.close()

def _load_weather_data_to_postgres():
    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn",
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    
    # โหลดข้อมูลจากไฟล์ JSON
    with open(os.path.join(DAG_FOLDER, "data.json"), "r") as f:
        data = json.load(f)

    # ดึงค่าที่ต้องการจาก JSON
    weather = data["data"]["current"]["weather"]
    timestamp = weather["ts"]
    temperature = weather["tp"]
    pressure = weather["pr"]
    humidity = weather["hu"]
    wind_speed = weather["ws"]
    wind_direction = weather["wd"]
    icon = weather["ic"]

    # ใช้ parameterized query เพื่อป้องกัน SQL Injection
    sql = """
        INSERT INTO weather_data (timestamp, temperature, pressure, humidity, wind_speed, wind_direction, icon) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (timestamp, temperature, pressure, humidity, wind_speed, wind_direction, icon))
    connection.commit()
    cursor.close()
    connection.close()


default_args = {
    "email": ["kan@odds.team"],
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}


with DAG(
    "AQI_api_dag",
    schedule="30 * * * *",
    start_date=timezone.datetime(2025, 3, 3),
    tags=["AQI"],
):
    start = EmptyOperator(task_id="start")

    get_AQI_data = PythonOperator(
        task_id="get_AQI_data",
        python_callable=_get_AQI_data,
    )

    validate_data = PythonOperator(
        task_id="validate_data",
        python_callable=_validate_data,
    )

    validate_AQI = PythonOperator(
        task_id="validate_AQI",
        python_callable=_validate_AQI,
    )

    create_pollution_data_table = PythonOperator(
        task_id="create_pollution_data_table",
        python_callable=_create_pollution_data_table,
    )

    create_weather_data_table = PythonOperator(
        task_id="create_weather_data_table",
        python_callable=_create_weather_data_table,
    )


    load_pollution_data_to_postgres = PythonOperator(
        task_id="load_pollution_data_to_postgres",
        python_callable=_load_pollution_data_to_postgres,
    )

    load_weather_data_to_postgres = PythonOperator(
        task_id="load_weather_data_to_postgres",
        python_callable=_load_weather_data_to_postgres,
    )
    send_email = EmailOperator(
        task_id="send_email",
        to=["kanin.di@rice.mmail.go.th"],
        subject="Finished getting open weather data",
        html_content="Done",
    )
    end = EmptyOperator(task_id="end")

    start >> get_AQI_data >> [validate_data ,validate_AQI] >> load_pollution_data_to_postgres >> load_weather_data_to_postgres >>send_email>> end
    start >> create_pollution_data_table >> create_weather_data_table >> load_pollution_data_to_postgres