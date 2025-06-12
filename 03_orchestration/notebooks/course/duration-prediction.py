#!/usr/bin/env python
# coding: utf-8
## Predict Taxi Trip Duration

# Necessary import
import pickle
import mlflow # for experiment tracking
import pandas as pd
import xgboost as xgb
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from pathlib import Path


# Set the tracking uri
mlflow.set_tracking_uri("http://127.0.0.1:5000") # where metadata are stored
# Set the experiment (creating it if doesn't exist)
mlflow.set_experiment("nyc-taxi-experiment")

# Folder path for saving models
models_folder = Path('models')
# Create the models folder
models_folder.mkdir(exist_ok = True)

# Function for wrangling the data
def read_dataframe(year, month):
    # URL address
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'
    # read parquet
    df = pd.read_parquet(url)

    # Feature Engineering
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime # target var
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60) # for minutes
    # Filtering durations
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    # Categorical features selection
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str) # convert integers to string

    # Feature Engineering to combine taxi trips origine and destination
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

    # return the dataframe
    return df

# Function for feature engineering
def create_X(df, dv = None):
    # Set feature variables
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    
    # Data dictionaries
    dicts = df[categorical + numerical].to_dict(orient = 'records')

    # For  training data
    if dv is None:
        # Initialize one-hot encoder
        dv = DictVectorizer(sparse = True)
        # Encoder training
        X = dv.fit_transform(dicts)
    # For validation data
    else:
        # One-Hot Encoding
        X = dv.transform(dicts)

    # return features and data preprocessor
    return X, dv

# Function for traning a ML model
def train_model(X_train, y_train, X_val, y_val, dv):
    # Start a new experiment run
    with mlflow.start_run() as run:
        # Prepare the data with XG-Boost special format
        train = xgb.DMatrix(X_train, label = y_train) # train
        valid = xgb.DMatrix(X_val, label = y_val) # val
    
        # XG-Boost Model optimal parameters
        best_params = {
            'learning_rate': 0.09585355369315604,
            'max_depth': 30,
            'min_child_weight': 1.060597050922164,
            'objective': 'reg:linear',
            'reg_alpha': 0.018060244040060163,
            'reg_lambda': 0.011658731377413597,
            'seed': 42
        }
    
        # Log the model parameters
        mlflow.log_params(best_params) # many parameters at once
    
        # Model training
        booster = xgb.train(
            params = best_params,
            dtrain = train,
            num_boost_round = 30,
            evals = [(valid, 'validation')],
            early_stopping_rounds = 50
        )
    
        # Make predictions
        y_pred = booster.predict(valid)
        # Compute the RMSE
        rmse = root_mean_squared_error(y_val, y_pred)
        # Log the model metric
        mlflow.log_metric("rmse", rmse)
    
        # Write a new binary file in the models folder
        with open("models/preprocessor.b", "wb") as f_out:
            # Save the encoder to that file
            pickle.dump(dv, f_out)
        # Log the encoder file as preprocessor
        mlflow.log_artifact("models/preprocessor.b", artifact_path = "preprocessor")
    
        # Log the XG-Boost model
        mlflow.xgboost.log_model(booster, artifact_path = "models_mlflow")    

    # Return the id of the experiment run
    return run.info.run_id

# Main function
def run(year, month):
    # Read the train dataset
    df_train = read_dataframe(year = year, month = month) # train
    # Get correct date for validation data
    next_year = year if month < 12 else year + 1 # year
    next_month = month + 1 if month < 12 else 1 # month
    # Read the validation dataset
    df_val = read_dataframe(year = next_year, month = next_month) # validation

    # Feature engineering
    X_train, dv = create_X(df_train) # train data
    X_val, _ = create_X(df_val, dv) # validaion data
    
    # Set the target variable
    target = 'duration'
    # Train and validation target vectors
    y_train = df_train[target].values # train
    y_val = df_val[target].values # validation

    # Model training
    run_id = train_model(X_train, y_train, X_val, y_val, dv)
    # Print the obtained run experiment id
    print(f"MLflow run_id: {run_id}")
    # return the run experiment id
    return run_id

# If the script is executed
if __name__ == "__main__":
    # import for parsing arguments
    import argparse

    # Initialize parser with a description
    parser = argparse.ArgumentParser(description = 'Train a model to predict taxi trip duration.')
    # Parse the year
    parser.add_argument('--year', type = int, required = True, help = 'Year of the data to train on')
    # Parse the month
    parser.add_argument('--month', type = int, required = True, help = 'Month of the data to train on')
    # Get the arguments parsed
    args = parser.parse_args()

    # Run the main function
    run_id = run(year = args.year, month = args.month)

    # Open a text file
    with open("run_id.txt", "w") as f:
        # Write the experiment run id
        f.write(run_id)
# ---