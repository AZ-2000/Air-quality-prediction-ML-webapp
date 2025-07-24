from flask import Flask, request, jsonify
import requests
# import xgboost as xgb
# import numpy as np
# import mlflow
# import mlflow.xgboost
# from datetime import datetime
# from prefect import flow, task
# from math import ceil
# from pandas import json_normalize
# import pandas as pd
from openaq import OpenAQ
# from xgboost import XGBRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, mean_absolute_error
import os
# from mlflow.tracking import MlflowClient
# import numpy as np
from openaq import OpenAQ
# from datetime import datetime
# from collections import defaultdict
# import faiss
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from pm25_pipeline import pm25_training_pipeline  
from pm25_pipeline import get_latest
from pm25_pipeline import search_pipeline
# m_client = MongoClient(os.getenv("MONGO_URI"))
# db = m_client["pm25"]
# collection = db["predictions"]
from pm25_pipeline import historical_data_pipeline

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
# mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
# mlflow.set_experiment(experiment_id=MLFLOW_EXPERIMENT_ID)
# mlflow.set_registry_uri(MLFLOW_REGISTRY_URI)

# client_ml = MlflowClient()
# experiment = client_ml.get_experiment(MLFLOW_EXPERIMENT_ID)
# mlflow.set_experiment(experiment.name)


client = OpenAQ(api_key=OPENAQ_API_KEY)
app = Flask(__name__)
CORS(app)  # This allows all origins by default

# @task
# def get_name(name_req):
#     response = client.locations.list(page=1, limit=100, radius=None, coordinates=None, bbox=None, providers_id=None, countries_id=None, parameters_id=None, licenses_id=None, iso="PK", monitor=None, mobile=None, order_by=None, sort_order=None)
#     for x in response.results:
#         if x.name == name_req:
#             return x
        

# @task
# def parameter_preprocessing(location):
#     params = []
#     pm25_sens_id = 0
#     s = 0
#     for i in location.sensors:
#         params.append(i.parameter.name)
#         if i.parameter.name == "pm25":
#             pm25_sens_id = location.sensors[s].id
#         s = s + 1
#     return pm25_sens_id
# @task
# def get_city_data(sens_id, datetime_one, datetime_two):
#     city_data = client.measurements.list(sensors_id = sens_id, datetime_from = datetime_one, datetime_to = datetime_two)
#     return city_data
# @task
# def pandas_convert(city_sens_data):
#     df_city= pd.DataFrame([{
#     'datetime': m.period.datetime_from.utc,
#     'pm25': m.value
# } for m in city_sens_data.results])

#     # Convert to datetime and sort
#     df_city['datetime'] = pd.to_datetime(df_city['datetime'])
#     df_city = df_city.sort_values('datetime').reset_index(drop=True)
    
#     # Set datetime as index
#     df_city.set_index('datetime', inplace=True)
    
#     # Create lag and rolling features
#     df_city['lag_1'] = df_city['pm25'].shift(1)
#     df_city['rolling_avg_3'] = df_city['pm25'].rolling(window=3).mean()
    
#     # Drop missing values caused by lag/rolling
#     df_city.dropna(inplace=True)
    
#     # Confirm the columns exist
#     return df_city

# @task
# def perform_xgboost(data_frame, city_name):
#     X = data_frame[['lag_1', 'rolling_avg_3']]
#     y = data_frame['pm25']
    
#     # Train-test split
#     X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    
#     # Train model
#     with mlflow.start_run():
#         model = XGBRegressor(objective='reg:squarederror')
#         model.fit(X_train, y_train)
        
#         # Predict and evaluate
#         y_pred = model.predict(X_test)
#         rmse = mean_squared_error(y_test, y_pred, squared=False)
#         mae = mean_absolute_error(y_test, y_pred)
#         mlflow.log_param("model_type", "XGBoost")
#         mlflow.log_param("features", ['lag_1', 'rolling_avg_3'])
#         mlflow.log_param("n_estimators", 100)
#         mlflow.log_param("learning_rate", 0.1)
#         mlflow.log_param("city", city_name)
        
#         mlflow.log_metric("rmse", rmse)
#         mlflow.log_metric("mae", mae)

#         # Log model to Databricks tracking server
#         mlflow.xgboost.log_model(model, artifact_path="model")

#         print(f"[MLflow] Model trained for {city_name} - RMSE: {rmse:.2f}, MAE: {mae:.2f}")
#         return rmse, mae
# @task
# def get_cities_with_pm25(param_id):
#     res = client.locations.list(page=1, limit=100, radius=None, coordinates=None, bbox=None, providers_id=None, countries_id=None, parameters_id=param_id, licenses_id=None, iso="PK", monitor=None, mobile=None, order_by=None, sort_order=None)
#     return res

# @task
# def id_list(cities):
#     sens_id = {}
#     sensor_list = []
#     pm25_sens_id = 0
#     s = 0
#     for i in cities.results:
#        for l in i.sensors:
#         if l.parameter.name == "pm25":
#            sens_id.update({i.name:l.id})
#            sensor_list.append(l.id)
#     return sensor_list
# @task
# def id_list_cities(cities):
#     sens_id = {}
#     sensor_list = []
#     pm25_sens_id = 0
#     s = 0
#     for i in cities.results:
#        for l in i.sensors:
#         if l.parameter.name == "pm25":
#            sens_id.update({i.name:l.id})
#            sensor_list.append(l.id)
#     return sens_id
# @task
# def get_city_data_avg(sensor_list, datetime_one, datetime_two):
#     df_city = pd.DataFrame()  # Initialize once outside the loop
#     s = 0
#     for sensor_id in sensor_list:
#         city_data = client.measurements.list(
#             sensors_id=sensor_id,
#             datetime_from=datetime_one,
#             datetime_to=datetime_two
#         )
#         # Create a DataFrame for this sensor
#         if not city_data.results:
#             continue

#         df_sensor = pd.DataFrame([{
#             'datetime': m.period.datetime_from.utc,
#             sensor_id: m.value
#         } for m in city_data.results])

#         # Convert to datetime and set as index
#         df_sensor['datetime'] = pd.to_datetime(df_sensor['datetime'])
#         df_sensor = df_sensor.sort_values('datetime').reset_index(drop=True)
#         df_sensor.set_index('datetime', inplace=True)

#         # Merge with main DataFrame
#         if df_city.empty:
#             df_city = df_sensor
#         else:
#             df_city = pd.merge(df_city, df_sensor, left_index=True, right_index=True, how='outer')

#     return df_city


    

# @flow(name="PM2.5 Training Pipeline")
# def pm25_training_pipeline(input_name: str,datetime_start: str, datetime_end: str):
#     city_name = get_name(input_name)
#     parameter = parameter_preprocessing(city_name)
#     city_data = get_city_data(parameter, datetime_start, datetime_end)
#     df = pandas_convert(city_data)
#     rmse, mae = perform_xgboost(df, city_name)
#     print(f"{city_name}: RMSE = {rmse:.2f}, MAE = {mae:.2f}")
    
    
    
@app.route('/train_model', methods=['POST'])
def train_model_post():
    data = request.json
    city = data.get('city')
    datetime_start = data.get('start_date')
    datetime_end = data.get('end_date')
    
    if not all([city, datetime_start, datetime_end]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        result = pm25_training_pipeline(city, datetime_start, datetime_end)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/history', methods=['POST'])
def history_post():
    data = request.json
    city = data.get('city')
    datetime_start = data.get('start_date')
    datetime_end = data.get('end_date')
    
    if not all([city, datetime_start, datetime_end]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        result = historical_data_pipeline(city, datetime_start, datetime_end)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search', methods=['POST'])
def search_post():
    data = request.json
    datetime_start = data.get('start_date')
    datetime_end = data.get('end_date')
    
    if not all([datetime_start, datetime_end]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        result = search_pipeline(datetime_start, datetime_end)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/get_latest', methods=['GET'])
def get_latest_data():
    try:
        city = request.args.get('city')  # Example: ?city=Lahore
        if not city:
            return jsonify({'error': 'City parameter is required'}), 400

        result = get_latest(city)
        return jsonify({"value":result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_cities', methods=['GET'])
def get_cities():
    city_docs = collection.find({}, {"_id": 0, "City_name": 1})
    cities = [doc["City_name"] for doc in city_docs]
    return jsonify(cities)


# -------------------- Flask Entry Point --------------------

if __name__ == '__main__':
    app.run(debug=True)
