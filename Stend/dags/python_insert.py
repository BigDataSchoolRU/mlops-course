import datetime
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, PythonVirtualenvOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.models import Variable
import os
import sys

sys.path.insert(0, 'dags/src/dataset/')
import connects
                    
default_args = {"owner": "dimon"}


# Python function
def insert_data_in_weather_table():
    engine = connects.get_PG_engine()
    with engine.connect() as conn:

        df = pd.read_csv('dags/data/datasets/weatherdata.csv')
        df.to_sql('weather', conn, if_exists='append', index=False)


        engine.dispose()


with DAG(
    dag_id="insert_data_in_weather_table",
    start_date=datetime.datetime(2022, 3, 10),
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
) as dag:

    first_task  = PythonOperator(task_id='insert_data_in_weather_table', python_callable=insert_data_in_weather_table)
    
    
    
    