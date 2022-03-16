import datetime

from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator


default_args = {"owner": "dimon"}

with DAG(
    dag_id="create_weather_table",
    start_date=datetime.datetime(2022, 3, 10),
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
) as dag:
    create_pet_table = PostgresOperator(
        task_id="create_weather_table",
        postgres_conn_id="database_PG",
        sql="""
            CREATE TABLE IF NOT EXISTS weather (
            timestamp TEXT ,
            temp FLOAT ,
            windspeed FLOAT ,
            humidity FLOAT ,
            precip FLOAT ,
            pressure FLOAT ,
            conditions TEXT ,
            dailyprecip TEXT ,
            dailysnow TEXT ,
            fog FLOAT ,
            rain FLOAT ,
            snow FLOAT );
          """,
    )