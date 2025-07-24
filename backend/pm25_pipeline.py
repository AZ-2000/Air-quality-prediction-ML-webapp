from flask import Flask, request, jsonify
import requests
import xgboost as xgb
import numpy as np
import mlflow
import mlflow.xgboost
from datetime import datetime
from prefect import flow, task
from math import ceil
from pandas import json_normalize
import pandas as pd
from openaq import OpenAQ
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os
from mlflow.tracking import MlflowClient
import numpy as np
from openaq import OpenAQ
from datetime import datetime
from collections import defaultdict
import faiss
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.metrics import mean_squared_error
import numpy as np
import sys
from datetime import datetime, timedelta
from itertools import islice

sys.stdout.reconfigure(encoding='utf-8', errors='replace')




load_dotenv()
m_client = MongoClient(os.getenv("MONGO_URI"))
print("this is the mongo client:" , m_client)
print("this is the mongo URI:" , os.getenv("MONGO_URI"))  # Debug: check this prints correctly
db = m_client["AQI_db"]
collection = db["Cities"]

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MLFLOW_REGISTRY_URI = os.getenv("databricks-uc")
MLFLOW_EXPERIMENT_ID = os.getenv("MLFLOW_EXPERIMENT_ID")


PREFECT_API_URL = os.getenv("PREFECT_API_URL")
PREFECT_API_KEY = os.getenv("PREFECT_API_KEY")

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
print(MLFLOW_EXPERIMENT_ID)
mlflow.set_experiment(experiment_id=MLFLOW_EXPERIMENT_ID)
mlflow.set_registry_uri(MLFLOW_REGISTRY_URI)

client_ml = MlflowClient()
experiment = client_ml.get_experiment(MLFLOW_EXPERIMENT_ID)
mlflow.set_experiment(experiment.name)


client = OpenAQ(api_key=OPENAQ_API_KEY)

@task 
def save_prediction(city, value):
    collection.insert_one({
        "city": city,
        "prediction": float(value),
        "timestamp": datetime.utcnow()
    })

@task
def get_name(name_req):
    response = client.locations.list(page=1, limit=100, radius=None, coordinates=None, bbox=None, providers_id=None, countries_id=None, parameters_id=None, licenses_id=None, iso="PK", monitor=None, mobile=None, order_by=None, sort_order=None)
    for x in response.results:
        if x.name == name_req:
            return x
        

@task
def parameter_preprocessing(location):
    params = []
    pm25_sens_id = 0
    s = 0
    for i in location.sensors:
        params.append(i.parameter.name)
        if i.parameter.name == "pm25":
            pm25_sens_id = location.sensors[s].id
        s = s + 1
    return pm25_sens_id
@task
def get_city_data(sens_id, datetime_one, datetime_two):
    city_data = client.measurements.list(sensors_id = sens_id, datetime_from = datetime_one, datetime_to = datetime_two)
    return city_data
@task
def pandas_convert(city_sens_data):
    df_city= pd.DataFrame([{
    'datetime': m.period.datetime_from.utc,
    'pm25': m.value
} for m in city_sens_data.results])

    # Convert to datetime and sort
    df_city['datetime'] = pd.to_datetime(df_city['datetime'])
    df_city = df_city.sort_values('datetime').reset_index(drop=True)
    
    # Set datetime as index
    df_city.set_index('datetime', inplace=True)
    
    # Create lag and rolling features
    df_city['lag_1'] = df_city['pm25'].shift(1)
    df_city['rolling_avg_3'] = df_city['pm25'].rolling(window=3).mean()
    
    # Drop missing values caused by lag/rolling
    df_city.dropna(inplace=True)
    
    # Confirm the columns exist
    return df_city

@task
def pandas_convert_historical(city_sens_data):
    df_city= pd.DataFrame([{
    'datetime': m.period.datetime_from.utc,
    'pm25': m.value
} for m in city_sens_data.results])

    # Convert to datetime and sort
    df_city['datetime'] = pd.to_datetime(df_city['datetime'])
    df_city = df_city.sort_values('datetime').reset_index(drop=True)
    
    # Set datetime as index
    df_city.set_index('datetime', inplace=True)
    
    # Create lag and rolling features
    # df_city['lag_1'] = df_city['pm25'].shift(1)
    # df_city['rolling_avg_3'] = df_city['pm25'].rolling(window=3).mean()
    
    # Drop missing values caused by lag/rolling
    df_city.dropna(inplace=True)
    
    df_city.reset_index(inplace=True)  # bring datetime back as a column
    results = df_city.sort_values("datetime")
    print(results)
    # 👇 Convert to list of dictionaries (JSON-ready for Flask)
    return results.to_dict(orient="records")

    

@task
def perform_xgboost(data_frame, city_name):
    data_frame = data_frame.reset_index()
    future_targets = {
        "pm25_t+1": "T+1",
        "pm25_t+2": "T+2",
        "pm25_t+3": "T+3"
    }

    data_frame['pm25_t+1'] = data_frame['pm25'].shift(-1)
    data_frame['pm25_t+2'] = data_frame['pm25'].shift(-2)
    data_frame['pm25_t+3'] = data_frame['pm25'].shift(-3)

    X = data_frame[['lag_1', 'rolling_avg_3']]
    results_df = []
 
    data_frame['datetime'] = pd.to_datetime(data_frame['datetime'], utc=False)
    first_day = data_frame['datetime'].dt.date.min()
    first_day_times = data_frame[data_frame['datetime'].dt.date == first_day]['datetime'].dt.time.tolist()
    last_day = data_frame['datetime'].dt.date.max()
    base_prediction_day = last_day + timedelta(days=1)

    for i, (target_col, horizon) in enumerate(future_targets.items()):
        y = data_frame[target_col]
        temp_df = pd.concat([X, y], axis=1).dropna()
        X_clean = temp_df[['lag_1', 'rolling_avg_3']]
        y_clean = temp_df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, shuffle=False, test_size=0.2)

        with mlflow.start_run():
            model = XGBRegressor(objective='reg:squarederror')
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)

            mlflow.log_param("model_type", "XGBoost")
            mlflow.log_param("features", ['lag_1', 'rolling_avg_3'])
            mlflow.log_param("horizon", horizon)
            mlflow.log_param("city", city_name)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mae", mae)
            mlflow.xgboost.log_model(model, artifact_path="model")

            print(f"[MLflow] Trained for {city_name} | Horizon: {horizon} | RMSE: {rmse:.2f}")

            prediction_day = base_prediction_day + timedelta(days=i)
            prediction_timestamps = [datetime.combine(prediction_day, t) for t in first_day_times]
            n_preds = min(len(y_pred), len(prediction_timestamps))

            prediction_subset = pd.DataFrame({
                "datetime": prediction_timestamps[:n_preds],
                "predicted_pm25": y_pred[:n_preds],
                "horizon": horizon
            })

            results_df.append(prediction_subset)

    combined_results = pd.concat(results_df).sort_values("datetime").reset_index(drop=True)

    # 👇 Convert to list of dictionaries (JSON-ready for Flask)
    return combined_results.to_dict(orient="records")
# @task
# def get_cities_with_pm25(param_id):
#     res = client.locations.list(page=1, limit=100, radius=None, coordinates=None, bbox=None, providers_id=None, countries_id=None, parameters_id=param_id, licenses_id=None, iso="PK", monitor=None, mobile=None, order_by=None, sort_order=None)
#     city_list = []
#     for x in res.results:
#         city_list.append(x.name)
#     return city_list
@task
def get_cityobj_with_pm25(param_id):
    res = client.locations.list(page=1, limit=100, radius=None, coordinates=None, bbox=None, providers_id=None, countries_id=None, parameters_id=param_id, licenses_id=None, iso="PK", monitor=None, mobile=None, order_by=None, sort_order=None)
    return res
@task
def id_list(cities):
    sens_id = {}
    sensor_list = []
    checked_cities = []
    for i in cities.results:
       if i.name in checked_cities:
            continue
       checked_cities.append(i.name)
       for l in i.sensors:
        if l.parameter.name == "pm25":
           sens_id.update({i.name:l.id})
           # print(i.name)
           sensor_list.append(l.id)
    print (len(checked_cities))
    return sensor_list[:20]
@task
def id_list_cities(cities):
    sens_id = {}
    sensor_list = []
    checked_cities = []
    for i in cities.results:
       if i.name in checked_cities:
           continue
       checked_cities.append(i.name)
       for l in i.sensors:
        if l.parameter.name == "pm25":
           sens_id.update({i.name:l.id})
           sensor_list.append(l.id)
    return sens_id
@task
def city_return_number(city_obj, number):
    city_listy = id_list_cities(city_obj)
    list_cities = dict(islice(city_listy.items(), number))
    return list_cities
@task
@task
def get_city_data_avg(sensor_list, datetime_one, datetime_two):
    df_city = pd.DataFrame()  # Initialize once outside the loop
    sensor_list = sensor_list[:20]
    for sensor_id in sensor_list:
        city_data = client.measurements.list(
            sensors_id=sensor_id,
            datetime_from=datetime_one,
            datetime_to=datetime_two
        )
        # Create a DataFrame for this sensor
        if not city_data.results:
            continue

        df_sensor = pd.DataFrame([{
            'datetime': m.period.datetime_from.utc,
            sensor_id: m.value
        } for m in city_data.results])

        # Convert to datetime and set as index
        df_sensor['datetime'] = pd.to_datetime(df_sensor['datetime'])
        df_sensor = df_sensor.sort_values('datetime').reset_index(drop=True)
        df_sensor.set_index('datetime', inplace=True)

        # Merge with main DataFrame
        if df_city.empty:
            df_city = df_sensor
        else:
            df_city = pd.merge(df_city, df_sensor, left_index=True, right_index=True, how='outer')
            
    df_city = df_city.fillna(0)

    return df_city
@task
def vector_convert(df_city):
    avg_values = df_city.mean(axis=0).to_numpy().astype('float32')
    vectors = avg_values.reshape(-1,1)
    return vectors
@task
def faiss_normalize(vectors):
    index = faiss.IndexFlatL2(1)  # dimension=1 for scalar average
    
    index.add(vectors)
    print(f"Added {index.ntotal} sensor average vectors to FAISS.")
    return index
@task
def reverse_dict(dict):
    reversed = {v:k for k,v in dict.items()}
    return reversed
@task
def query_similar_cities(city_name, index, vectors, list_cities, sensor_to_city, sensor_columns, threshold):
    # Map city name to sensor ID
    sensor_id = list_cities.get(city_name)
    if sensor_id is None:
        print(f"City '{city_name}' not found in list_cities.")
        return []

    # Find sensor ID index in sensor_columns (all sensor IDs in your DataFrame)
    if sensor_id not in sensor_columns:
        print(f"Sensor ID '{sensor_id}' not found in DataFrame columns.")
        return []

    sensor_idx = sensor_columns.index(sensor_id)
    query_vector = vectors[sensor_idx].reshape(1, -1)

    # Query all sensors
    D, I = index.search(query_vector, k=len(sensor_columns))

    matches = []
    for dist, idx in zip(D[0], I[0]):
        if dist <= threshold**2 :
            matched_sensor_id = sensor_columns[idx]
            matched_city = sensor_to_city.get(matched_sensor_id,"Unknown")
            print(matched_sensor_id)
            if np.sqrt(dist) != 0:
                matches.append((matched_city, round(float(np.sqrt(dist)), 2)))
    print(matches)
    matches = sorted(matches, key=lambda x: x[1], reverse=False)
    print(matches)
    filtered_matches = [
    (city, value) for city, value in matches
    if city not in {"US Diplomatic Post: Lahore", "Unknown"}
    ]   
    # documents = [{"City_name": city} for city, _ in filtered_matches]
    # collection.insert_many(documents)
    filtered_matches = filtered_matches[:4]
    print(filtered_matches)
    return [(city, float(distance)) for city, distance in filtered_matches]

@flow(name="searchengine")
def search_pipeline(datetime_start: str, datetime_end: str):
    cityobj = get_cityobj_with_pm25(2)
    id_listy = id_list(cityobj)
    new_list = city_return_number(cityobj,10)
    data_frame_avg = get_city_data_avg(id_listy,datetime_start, datetime_end)
    vectors = vector_convert(data_frame_avg)
    ind = faiss_normalize(vectors)
    reversed = reverse_dict(new_list)
    matched_data = query_similar_cities("Lahore", ind, vectors,new_list, reversed, id_listy, threshold = 10)
    return matched_data    
    
    
@flow(name="PM2.5 Training Pipeline")
def pm25_training_pipeline(input_name: str,datetime_start: str, datetime_end: str):
    city_name = get_name(input_name)
    parameter = parameter_preprocessing(city_name)
    city_data = get_city_data(parameter, datetime_start, datetime_end)
    df = pandas_convert(city_data)
    pred_result = perform_xgboost(df, city_name)
    return pred_result

@flow(name = "Historical Data")
def historical_data_pipeline(input_name: str, datetime_start:str, datetime_end:str):
    city_name = get_name(input_name)
    parameter= parameter_preprocessing(city_name)
    city_data = get_city_data(parameter,datetime_start, datetime_end)
    dict = pandas_convert_historical(city_data)
    return dict
    
    
@flow(name ="latest values")
def get_latest(name):
    loc = get_name(name)
    latest_p = parameter_preprocessing(loc)
    latest_loc = client.locations.latest(loc.id)
    latest_results = latest_loc.results
    for x in latest_results:
        if x.sensors_id == latest_p:
            if x.value > 0:
                latest_val = x.value
                print (x.value)
    return latest_val
    