This repository contains the code to an air quality prediction webapp 
that uses xgboost for numerical prediction of PM 2.5 concentration in Pakistani cities.
ML-flow and Prefect are used for pipelining and logging parameters for training.

OpenAQ's api was used to fetch the data. Re-charts was used for visualization and the application is hosted on react

The cities for the dropdown menu were fetched from mongoDB

The prediction model could only utilize data from the past 3 days owing to rate limiting issues with the API

