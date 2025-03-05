# DPU-AQI
# IQA
1.Ceate  Repositories on Github

2.สร้างไฟล์ docker-compose.yml coppy จาก https://raw.githubusercontent.com/zkan/dpu-modern-data-pipelines/refs/heads/main/docker-compose.yaml

3.สร้าง ไฟล์/ โฟเดอร์  

โฟเดอร์ 
mkdir -p weather
สร้าง ไฟล์
.gitignore
__pycache__
logs
*.json

4.เปิดสิทธิ์ให้ docker เข้าถึงไฟล์  echo -e "AIRFLOW_UID=$(id -u)" > .env 

5. run docker คำสั้ง docker compose up 

6.API AQI

6.1 สมัครสมาชิก https://www.iqair.com/th/air-quality-monitors/api

6.2 สร้าง API key https://dashboard.iqair.com/personal/api-keys

6.3 set  Variable API_KEY   ใน Airflow

6.4 API  http://api.airvisual.com/v2/......"+ API_KEY

7. validate data
   
8. Connections and Hooks
ให้เราไปที่เมนู Admin และเข้าไปที่ Connections
เสร็จแล้วกดปุ่ม + สีน้ำเงินเพื่อเพิ่ม Connection หลังจากนั้นให้เรากรอกข้อมูลของ Postgres database ของเราลงไป 
โดยในที่นี้ให้กรอก
- Connection Id: `my_postgres_conn`
- Connection Type: `Postgres`
- Host: `db`
- Schema: `postgres`
- Login: `postgres`
- Password: `postgres`
- Port: `5432`
พอกรอกเสร็จ ก็ให้เรากดปุ่ม Save
  
9.create table

10.load data to postgres

11.dbt

11.1 dbt init

Enter a name for your project 

Which database would you like to use?  เลือก postgres (1)

host (hostname for the instance): localhost

port [5432]

user (dev username): postgres

pass (dev password):

dbname (default database that dbt will build objects in): postgres

schema (default schema that dbt will build objects in): dbt_AQI

threads (1 or more) [1]: 

11.2 mv /home/codespace/.dbt/profiles.yml AQI/

11.3  docker compse up

11.4 dbt debug

12.dbt run

13._src.yml
sources:
  - name: AQI
    database: postgres
    schema: public
    tables:
      - name: pollution_data
      - name: weather_data

14. _models.yml

version: 2

models:
  - name: stg_pollution_data
    description: Staging pollution data is Air quality index (AQI⁺) and PM2.5 air pollution  
    columns:
      - name: id
        description: integer Auto Increment
      - name: timestamp
        description: timestamp
      - name: aqius
        description: AQI value based on US EPA standard
      - name: mainus
        description: main pollutant for US AQI       
      - name: aqicn
        description: AQI value based on China MEP standard
      - name: mainus
        description: main pollutant for Chinese AQI  

15. dbt docs generate

16. dbt docs serve --port 9090
