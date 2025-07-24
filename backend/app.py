from flask import Flask, request, jsonify
import requests
from openaq import OpenAQ
import os
from openaq import OpenAQ
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from pm25_pipeline import pm25_training_pipeline  
from pm25_pipeline import get_latest
from pm25_pipeline import search_pipeline

from pm25_pipeline import historical_data_pipeline

load_dotenv()
m_client = MongoClient(os.getenv("MONGO_URI"))
print("this is the mongo client:" , m_client)
print("this is the mongo URI:" , os.getenv("MONGO_URI"))  
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



client = OpenAQ(api_key=OPENAQ_API_KEY)
app = Flask(__name__)
CORS(app)  

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


if __name__ == '__main__':
    app.run(debug=True)
