# Necessary import
# for handling data
import datetime
import time
import random
import logging   
import pandas as pd  
import psycopg
import joblib

# for orchestration
from prefect import task, flow
# for monitoring
from evidently import Report
from evidently import DataDefinition
from evidently import Dataset
from evidently.metrics import ValueDrift, DriftedColumnsCount, MissingValueCount

# Specify how to load the database
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# Global variable
SEND_TIMEOUT = 10
rand = random.Random()

# Satement for creating a table
create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
)
"""

# Read the reference data
reference_data = pd.read_parquet('data/reference.parquet')
# Open the model file
with open('models/lin_reg.bin', 'rb') as f_in:
	model = joblib.load(f_in) # model loading

# Read the February data
raw_data = pd.read_parquet('data/green_tripdata_2022-02.parquet')

# Date time for the begining of February
begin = datetime.datetime(2022, 2, 1, 0, 0)
# Subset of features
num_features = ['passenger_count', 'trip_distance', 'fare_amount', 'total_amount'] # numerical
cat_features = ['PULocationID', 'DOLocationID'] # categorical
# Set the data definition
data_definition = DataDefinition(
    numerical_columns = num_features + ['prediction'],
    categorical_columns = cat_features
)

# Build a report
report = Report(metrics = [
    ValueDrift(column = 'prediction'),
    DriftedColumnsCount(),
    MissingValueCount(column = 'prediction')
])

# Connection info for the postgres database
CONNECTION_STRING = "host=localhost port=5432 user=postgres password=example"
# Connection info for the test database
CONNECTION_STRING_DB = CONNECTION_STRING + " dbname=test"

# Task function to prepare the database
@task
def prep_db():
	# Open a connection to the database
	with psycopg.connect(CONNECTION_STRING, autocommit = True) as conn:
		# Execute a SQL query
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		# If no database
		if len(res.fetchall()) == 0:
			conn.execute("create database test;") # create it
		# Connect to the database
		with psycopg.connect(CONNECTION_STRING_DB) as conn:
			conn.execute(create_table_statement) # create a table

# Task function for calculating daily metrics
@task
def calculate_metrics_postgresql(i):
	# Get the current data -> the data from February start to the current day
	current_data = raw_data[(raw_data.lpep_pickup_datetime >= (begin + datetime.timedelta(i))) &
		(raw_data.lpep_pickup_datetime < (begin + datetime.timedelta(i + 1)))]

	# current_data.fillna(0, inplace = True) -> filling missing values can be done while predicting
	# Make predictions
	current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))

	# Prepare the data for reporting
	current_dataset = Dataset.from_pandas(current_data, data_definition = data_definition) # current data
	reference_dataset = Dataset.from_pandas(reference_data, data_definition = data_definition) # reference data

	# Run the report
	run = report.run(reference_data = reference_dataset, current_data = current_dataset)
	# Get the report as dictionary
	result = run.dict()

	# Extract metrics
	prediction_drift = result['metrics'][0]['value']
	num_drifted_columns = result['metrics'][1]['value']['count']
	share_missing_values = result['metrics'][2]['value']['share']
	# Connect to the database
	with psycopg.connect(CONNECTION_STRING_DB, autocommit = True) as conn:
		# Use a cursor
		with conn.cursor() as curr:
			# Insert metrics values into the table
			curr.execute(
				"insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
				(begin + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values)
			)

# Main function 
@flow
def batch_monitoring_backfill():
	prep_db() # prepare the database
	# Calculate last time the data was sent
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	# For each day of february
	for i in range(0, 27):
		# Compute the daily metrics
		calculate_metrics_postgresql(i)

		# Calculate the time to wait for simulating the real production usage
		# New send date time
		new_send = datetime.datetime.now()
		# Time elapsed since the last sent
		seconds_elapsed = (new_send - last_send).total_seconds()
		# If the sending time out is less than our time out
		if seconds_elapsed < SEND_TIMEOUT:
			# We wait for the rest time
			time.sleep(SEND_TIMEOUT - seconds_elapsed)
		# Update our last sent
		while last_send < new_send:
			last_send = last_send + datetime.timedelta(seconds = 10)
		# Inform that the data was sent
		logging.info("data sent")

# If the script is executed
if __name__ == '__main__':
	# run the flow
	batch_monitoring_backfill()   