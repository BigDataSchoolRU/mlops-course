from pathlib import Path
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.insert(0, os.getcwd())
import dataset.connects as connects

def get_train_test_datasets(data_path, train_path, test_path, train_size=0.8):
    '''
    Получает данные из data_path (csv файл)
    Обрабатывает и сохраняет train и test выборки в train_path и test_path соответственно
    '''
    
    df_weather = pd.read_csv(data_path)
    
    # in_columns
    datetime_column = 'timestamp'
    float_columns = ['temp', 'windspeed', 'humidity', 'precip', 'pressure',
                     'dailyprecip', 'dailysnow', 'fog', 'rain', 'snow']
    categorical_columns = ['conditions']
    dummy_columns = ['conditions_Clear', 'conditions_Haze', 'conditions_Heavy Rain',
                     'conditions_Heavy Snow', 'conditions_Light Freezing Fog',
                     'conditions_Light Freezing Rain', 'conditions_Light Rain',
                     'conditions_Light Snow', 'conditions_Mostly Cloudy',
                     'conditions_Overcast', 'conditions_Partly Cloudy', 'conditions_Rain',
                     'conditions_Scattered Clouds', 'conditions_Snow', 'conditions_Unknown']
    
    # train columns
    in_features = ['temp', 'windspeed', 'humidity', 'precip', 'pressure',
                   'dailyprecip', 'dailysnow', 'fog', 'rain', 'snow',
                   
                   'conditions_Clear', 'conditions_Haze', 'conditions_Heavy Rain',
                   'conditions_Heavy Snow', 'conditions_Light Freezing Fog',
                   'conditions_Light Freezing Rain', 'conditions_Light Rain',
                   'conditions_Light Snow', 'conditions_Mostly Cloudy',
                   'conditions_Overcast', 'conditions_Partly Cloudy', 'conditions_Rain',
                   'conditions_Scattered Clouds', 'conditions_Snow', 'conditions_Unknown',
                   
                   'windspeed_roll_5']
    target = 'windspeed_target'
    
    # datetime processing
    df_weather[datetime_column] = df_weather[datetime_column].map(lambda s: datetime.fromisoformat(s))
    df_weather.sort_values(datetime_column, inplace=True)
    df_weather.index = df_weather[datetime_column]
    df_weather.index.name = 'index'
    df_weather.drop(['timestamp'], axis=1, inplace=True)
    
    # float processing
    df_weather['dailysnow'] = df_weather['dailysnow'].apply(lambda x: 0. if x=='T' else x)
    df_weather['dailyprecip'] = df_weather['dailyprecip'].apply(lambda x: 0. if x=='T' else x)
    df_weather['dailysnow'] = df_weather['dailysnow'].astype(float) 
    df_weather['dailyprecip'] = df_weather['dailyprecip'].astype(float) 
    
    df_weather['windspeed'] = df_weather['windspeed'].fillna(method='backfill')
    df_weather['windspeed'] = df_weather['windspeed'].fillna(method='ffill')
    df_weather['windspeed'] = df_weather['windspeed'].fillna(0.)
    
    df_weather['pressure'] = df_weather['pressure'].fillna(method='backfill')
    df_weather['pressure'] = df_weather['pressure'].fillna(method='ffill')
    
    df_weather[float_columns] = df_weather[float_columns].astype(float)

    # categorical processing
    columns_before = list(df_weather.columns)
    df_weather = pd.get_dummies(df_weather, columns=categorical_columns)
    df_weather = df_weather.reindex(columns = columns_before + dummy_columns, fill_value=0)
    
    # add 'windspeed_roll_5'
    df_weather['windspeed_roll_5'] = df_weather['windspeed'].rolling(5).mean()
    
    # save only in_features
    df_weather = df_weather[in_features]
    
    # create target
    df_weather[target] = df_weather['windspeed'].shift(-2)
    
    # drop nan
    df_weather = df_weather.dropna()
    
    data_train = df_weather[:int(df_weather.shape[0] * train_size)]
    data_test = df_weather[int(df_weather.shape[0] * train_size):]
    
    data_train.to_csv(train_path)
    data_test.to_csv(test_path)


def get_data_PG(datetime_start, datetime_end):

    engine = connects.get_PG_engine()
    with engine.connect() as conn:

        query = f'''
        SELECT * FROM public.weather
        where "timestamp" >= '{datetime_start}'
        and "timestamp" < '{datetime_end}'
        '''
        
        df_weather = pd.read_sql(query, conn)
        
        engine.dispose()

 # in_columns
    datetime_column = 'timestamp'
    float_columns = ['temp', 'windspeed', 'humidity', 'precip', 'pressure',
                     'dailyprecip', 'dailysnow', 'fog', 'rain', 'snow']
    categorical_columns = ['conditions']
    dummy_columns = ['conditions_Clear', 'conditions_Haze', 'conditions_Heavy Rain',
                     'conditions_Heavy Snow', 'conditions_Light Freezing Fog',
                     'conditions_Light Freezing Rain', 'conditions_Light Rain',
                     'conditions_Light Snow', 'conditions_Mostly Cloudy',
                     'conditions_Overcast', 'conditions_Partly Cloudy', 'conditions_Rain',
                     'conditions_Scattered Clouds', 'conditions_Snow', 'conditions_Unknown']
    
    # train columns
    in_features = ['temp', 'windspeed', 'humidity', 'precip', 'pressure',
                   'dailyprecip', 'dailysnow', 'fog', 'rain', 'snow',
                   
                   'conditions_Clear', 'conditions_Haze', 'conditions_Heavy Rain',
                   'conditions_Heavy Snow', 'conditions_Light Freezing Fog',
                   'conditions_Light Freezing Rain', 'conditions_Light Rain',
                   'conditions_Light Snow', 'conditions_Mostly Cloudy',
                   'conditions_Overcast', 'conditions_Partly Cloudy', 'conditions_Rain',
                   'conditions_Scattered Clouds', 'conditions_Snow', 'conditions_Unknown',
                   
                   'windspeed_roll_5']
    
    # datetime processing
    df_weather[datetime_column] = df_weather[datetime_column].map(lambda s: datetime.fromisoformat(s))
    df_weather.sort_values(datetime_column, inplace=True)
    df_weather.index = df_weather[datetime_column]
    df_weather.index.name = 'index'
    df_weather.drop(['timestamp'], axis=1, inplace=True)
    
    # float processing
    df_weather['dailysnow'] = df_weather['dailysnow'].apply(lambda x: 0. if x=='T' else x)
    df_weather['dailyprecip'] = df_weather['dailyprecip'].apply(lambda x: 0. if x=='T' else x)
    df_weather['dailysnow'] = df_weather['dailysnow'].astype(float) 
    df_weather['dailyprecip'] = df_weather['dailyprecip'].astype(float) 
    
    df_weather['windspeed'] = df_weather['windspeed'].fillna(method='backfill')
    df_weather['windspeed'] = df_weather['windspeed'].fillna(method='ffill')
    df_weather['windspeed'] = df_weather['windspeed'].fillna(0.)
    
    df_weather['pressure'] = df_weather['pressure'].fillna(method='backfill')
    df_weather['pressure'] = df_weather['pressure'].fillna(method='ffill')
    
    df_weather[float_columns] = df_weather[float_columns].astype(float)

    # categorical processing
    columns_before = list(df_weather.columns)
    df_weather = pd.get_dummies(df_weather, columns=categorical_columns)
    df_weather = df_weather.reindex(columns = columns_before + dummy_columns, fill_value=0)
    
    # add 'windspeed_roll_5'
    df_weather['windspeed_roll_5'] = df_weather['windspeed'].rolling(5).mean()
    
    # save only in_features
    df_weather = df_weather[in_features]

    return df_weather


