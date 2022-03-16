from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# грузим переменные окружения
dotenv_path = os.path.join('../../../database.env')
if os.path.exists(dotenv_path):
    print('load_dotenv')
    load_dotenv(dotenv_path)
else:
    print(f'No have dotenv file in "{dotenv_path}"')

PG_USER = os.environ.get('POSTGRES_USER')
PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
PG_DB = os.environ.get('POSTGRES_DB')
PG_HOST = os.environ.get('POSTGRES_HOST')
PG_PORT = os.environ.get('POSTGRES_PORT')


# коннекст к Postgres
def get_PG_engine():
    engine = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}')
    return engine