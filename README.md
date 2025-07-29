This repository contains the code to an air quality prediction webapp 
that uses xgboost for numerical prediction of PM 2.5 concentration in Pakistani cities.
ML-flow and Prefect are used for pipelining and logging parameters for training.

OpenAQ's api was used to fetch the data. Re-charts was used for visualization and the application is hosted on react

The cities for the dropdown menu were fetched from mongoDB

The prediction model could only utilize data from the past 3 days owing to rate limiting issues with the API

FAISS was used to normalize and store the vectors at runtime and k-nn was used to search for cities with similar air quality indexes by calculating over their historical values. The average of those historical values were then used to calculate the similarity in terms of average air quality in terms of PM2.5 concentrations over a period of time

Databricks/MLflow was used to log the parameters such as RMSE and MAE and this application was deployed on prefect to ensure end-to-end pipelining and deployment
