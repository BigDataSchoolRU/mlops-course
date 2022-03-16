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
import mlflow
from mlflow.tracking.client import MlflowClient
import mlflow.pyfunc
import pickle5 as pickle
 
# Указываем доступ в БД
sql_string = "postgresql://unicorn_user:magical_password@host.docker.internal:7432/rainbow_database"
mlflow.set_tracking_uri(sql_string)
# Задаем имя модели
model_name = "lin_regr_wind"
# Создаем mlflow клиента
client = MlflowClient()
# Подтянем последнюю production модель с таким названием 
latest_version_info = client.get_latest_versions(model_name, stages=["Production"])
latest_production_version = latest_version_info[0].version

# model_version_uri = client.get_model_version_download_uri(model_name, latest_production_version)
model_version_uri = 'dags/mlflow-artifact-location/9197702b4db74fd5bd2965403285ee59/artifacts/model'
print("Loading registered model version from URI: '{model_uri}'".format(model_uri=model_version_uri))
model_from_mlflow = mlflow.pyfunc.load_model(model_version_uri)

# model_path_mlflow='dags/mlflow-artifact-location/9197702b4db74fd5bd2965403285ee59/artifacts/model/model.pkl'
# with open(model_path_mlflow, 'rb') as f:
#     model_from_mlflow = pickle.load(f)

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

    # predict = linear_regression.predict_linear_regression(df_weather, MODEL_PATH)
    predict = model_from_mlflow.predict(df_weather)
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
    dag_id="predict_weather_mlflow",
    default_args=default_args,
    # catchup=False,
) as dag:

    first_task  = PythonOperator(task_id='predict_weather', python_callable=predict_weather, 
                                provide_context=True,
                                dag=dag)
    
    
    
    