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
import weather_prepare
sys.path.insert(0, 'dags/src/models/')
import linear_regression
                    
default_args = {"owner": "dimon", 
                "depends_on_past": False, 
                "start_date": datetime.datetime(2022, 3, 12),
                "schedule_interval":"00 10 * * *",
                "retries": 1,
                "retry_delay": datetime.timedelta(minutes=1)}

MODEL_PATH = 'dags/models/linear_regression.pickle'

# Python function
def predict_weather(**kwargs):

    execution_date = kwargs["execution_date"]
    execution_date = datetime.datetime.fromtimestamp(execution_date.timestamp())
    print(f'execution_date = {execution_date}')
    datetime_start = '2016-06-30 23:51:00'
    datetime_end = '2016-07-01 23:51:00'
    df_weather = weather_prepare.get_data_PG(datetime_start, datetime_end)
    df_weather = df_weather.iloc[-1:]

    predict = linear_regression.predict_linear_regression(df_weather, MODEL_PATH)
    df_weather['windspeed_predict'] = predict
    df_weather['timestamp'] = df_weather.index
    df_weather['timestamp'] += datetime.timedelta(hours=2)
    
    df_predict = df_weather[['timestamp', 'windspeed_predict']].copy()
    print('tut3', df_predict)

    engine = connects.get_PG_engine()
    with engine.connect() as conn:
        df_predict.to_sql('weather_predict', conn, if_exists='append', index=False)

        engine.dispose()


with DAG(
    dag_id="predict_weather",
    default_args=default_args,
    # catchup=False,
) as dag:

    first_task  = PythonOperator(task_id='predict_weather', python_callable=predict_weather, 
                                provide_context=True,
                                dag=dag)
    
    
    
    