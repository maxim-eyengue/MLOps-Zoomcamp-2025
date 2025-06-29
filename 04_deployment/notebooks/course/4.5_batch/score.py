#!/usr/bin/env python
# coding: utf-8

# Necessary import
import sys
import uuid
import mlflow  
import pandas as pd 

from pathlib import Path
from datetime import datetime  
from prefect import task, flow, get_run_logger 
from prefect.context import get_run_context
from dateutil.relativedelta import relativedelta  


# Function to generate ride IDs
def generate_uuids(n):
    ride_ids = []
    for i in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids


# Function for reading the data
def read_dataframe(filename: str):
    # read the parquet file
    df = pd.read_parquet(filename)

    # Feature engineering to create a duration column
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    # Convert durations to minutes
    df.duration = df.duration.dt.total_seconds() / 60
    # Filter durations
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    # Set the ride ID
    df['ride_id'] = generate_uuids(len(df))
    return df # to return the prepared dataframe

# Function for building data dictionaries
def prepare_dictionaries(df: pd.DataFrame):
    # Set of categorical features
    categorical = ['PULocationID', 'DOLocationID']
    # Convert categorical features to string
    df[categorical] = df[categorical].astype(str)
    
    # Create a trajet feature
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    # Set of features
    categorical = ['PU_DO'] # categorical
    numerical = ['trip_distance'] # numerical
    # Build the data dictionaries
    dicts = df[categorical + numerical].to_dict(orient = 'records')
    return dicts # to return dictionaries

# Function for loading the model
def load_model(run_id):
    # Get the model URI
    logged_model = f'mlflow-models/1/{run_id}/artifacts/model' # f's3://mlflow-models-alexey/1/{run_id}/artifacts/model'
    # Load and return the model
    model = mlflow.pyfunc.load_model(logged_model)
    return model 

# Function for saving the results to a data frame
def save_results(df, y_pred, run_id, output_file):
    # Build a dataframe with input and predictions information
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id

    # Save the result dataframe
    df_result.to_parquet(output_file, index = False)

# Function for applying the model
@task
def apply_model(input_file, run_id, output_file):
    logger = get_run_logger()

    logger.info(f'reading the data from {input_file}...')
    df = read_dataframe(input_file)
    dicts = prepare_dictionaries(df)

    logger.info(f'loading the model with RUN_ID={run_id}...')
    model = load_model(run_id)

    logger.info(f'applying the model...')
    y_pred = model.predict(dicts)

    logger.info(f'saving the result to {output_file}...')

    save_results(df, y_pred, run_id, output_file)
    return output_file

# Function for data paths
def get_paths(run_date, taxi_type, run_id):
    prev_month = run_date - relativedelta(months = 1)
    year = prev_month.year
    month = prev_month.month 

    # Input data address
    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    # f's3://nyc-tlc/trip data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    # Address of the output
    output_file = f'output/{taxi_type}/{year:04d}-{month:02d}-{run_id}.parquet'
    # f's3://nyc-duration-prediction-alexey/taxi_type={taxi_type}/year={year:04d}/month={month:02d}/{run_id}.parquet'

    # Input and output files data paths
    return input_file, output_file


# Function for predicting ride durations
@flow
def ride_duration_prediction(
        taxi_type: str,
        run_id: str,
        run_date: datetime = None):
    if run_date is None:
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time
    
    input_file, output_file = get_paths(run_date, taxi_type, run_id)

    apply_model(
        input_file=input_file,
        run_id=run_id,
        output_file=output_file
    )


# Main function
def run():
    # Script parameterization
    taxi_type = sys.argv[1] # 'green'
    year = int(sys.argv[2]) # 2021
    month = int(sys.argv[3]) # 3
    run_id = sys.argv[4] # '1ca05c6d23f44066a4a4dcdbe1639de4'
    
    # Folder path for saving results
    output_folder = Path(f'output/{taxi_type}')
    # Create the results folder
    output_folder.mkdir(exist_ok = True)

    # Make ride duration prediction
    ride_duration_prediction(
        taxi_type = taxi_type,
        run_id = run_id,
        run_date = datetime(year = year, month = month, day = 1)
    )

# If the script is executed
if __name__ == '__main__':
    # Run the main function
    run()
