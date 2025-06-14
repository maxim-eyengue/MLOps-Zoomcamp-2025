#!/usr/bin/env python
# coding: utf-8

## Predict Taxi Trip Duration
# Necessary import
import mlflow # for experiment tracking
import pandas as pd
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from prefect import flow, task


# Function for wrangling the data
@task(retries = 3, retry_delay_seconds = 2)
def read_dataframe(filename):
    """Read Green taxi trip data into DataFrame"""
    # read parquet
    df = pd.read_parquet(filename)

    # Print data size before preprocessing
    print(f"Number of rows before preprocessing: {len(df)}.")

    # Feature engineering for creating the duration column
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    # Convert durations into minutes
    df.duration = df.duration.dt.total_seconds() / 60

    # Filtering for trips lasting from 1 min to 1 hour
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    # Categorical features
    categorical = ['PULocationID', 'DOLocationID']
    # Convert categorival variables to string
    df[categorical] = df[categorical].astype(str)

    # Print data size after preprocessing
    print(f"Number of rows after preprocessing: {len(df)}.")

    # return the dataframe
    return df


# Function for traning a ML model
@task(log_prints = True)
def train_model(df):
    """Train a Linear Regression model"""
    # Start a new experiment run
    with mlflow.start_run() as run:
        # Set a tag to know who worked on the project
        mlflow.set_tag("developer", "Maximilien")

        # Subset features
        features = ["PULocationID", "DOLocationID"]
        # Train data dictionaries - with ids as strings for one-hot encoding
        train_dicts = df[features].astype(str).to_dict(orient = 'records')

        # Initialize the dictionary vectorizer
        dv = DictVectorizer()
        # Fit the vectorizer getting a feature matrix
        X_train = dv.fit_transform(train_dicts)
        # Target vector
        y_train = df["duration"].values

        # Initialize linear regressor
        lr = LinearRegression()
        # Train model
        lr.fit(X_train, y_train)

        # Make training predictions
        y_pred = lr.predict(X_train)

        # RMSE metric
        rmse = root_mean_squared_error(y_train, y_pred)
        # Log the metric
        mlflow.log_metric("rmse", rmse)

        # return the model
        return dv, lr


@task(log_prints = True)
def register_model():
    """Function to register the model"""
    # Set MLFlow client
    client = MlflowClient()
    # Retrieve the top_n model runs and log the models
    experiment = client.get_experiment_by_name("nyc-taxi-experiment")
    # Get run
    run_id = client.search_runs(
        experiment_ids = experiment.experiment_id,
        run_view_type = ViewType.ACTIVE_ONLY,
        max_results = 1,
        order_by = ["metrics.rmse ASC"] # best model on test rmse
    )[0].info.run_id
    # Register the best model
    mlflow.register_model(model_uri = f"runs:/{run_id}/model",
                          name = "nyc-yellow-taxi-regressor")
        

# Main function
@flow
def main_flow(filename):
    """The Main Training Pipeline"""
    # Set the tracking uri
    mlflow.set_tracking_uri("http://127.0.0.1:5000") # where metadata are stored
    # Set the experiment (creating it if doesn't exist)
    mlflow.set_experiment("nyc-taxi-experiment")

    # Autolog with mlflow
    mlflow.sklearn.autolog()
    # Read the train dataset
    df_train = read_dataframe(filename) # train
    # Model training
    _, model = train_model(df_train)
    # Print the obtained run experiment id
    print(f"Model Intercept: {round(model.intercept_, 2)}")
    # register the model
    register_model()



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
 
    # URL address
    filename = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{args.year}-{args.month:02d}.parquet'
    # Run the main function
    main_flow(filename)
# ---