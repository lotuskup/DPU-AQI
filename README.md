# DPU-AQI
# IQA
1.Ceate  Repositories on Github

2.สร้างไฟล์ docker-compose.yml coppy จาก https://raw.githubusercontent.com/zkan/dpu-modern-data-pipelines/refs/heads/main/docker-compose.yaml

3.สร้าง โฟเดอร์ เก็บงาน mkdir -p weather

4.เปิดสิทธิ์ให้ docker เข้าถึงไฟล์  echo -e "AIRFLOW_UID=$(id -u)" > .env 

5.docker compose up 

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

11.

