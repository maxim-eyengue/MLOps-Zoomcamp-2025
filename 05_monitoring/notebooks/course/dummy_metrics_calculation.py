# Necessary import
import datetime
import time
import random
import logging # for adding information in the terminal
import uuid
import pytz # for time zone
import psycopg # for postgres dataabases

# Specify how to load the database
logging.basicConfig(level = logging.INFO, format = "%(asctime)s [%(levelname)s]: %(message)s")

# Global variables
SEND_TIMEOUT = 10
rand = random.Random()

# Satement for creating a table
create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	value1 integer,
	value2 varchar,
	value3 float
)
"""

# Function to prepare the database
def prep_db():
	# Open a connection to the database
	with psycopg.connect("host=localhost port=5432 user=postgres password=example", autocommit = True) as conn:
		# Execute a SQL query
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		# If no database
		if len(res.fetchall()) == 0:
			conn.execute("create database test;") # create it
		# Connect to the database
		with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn:
			conn.execute(create_table_statement) # create a table

# Function for calculating dummy metrics
def calculate_dummy_metrics_postgresql(curr): # curr: position of the cursor where to add values
	value1 = rand.randint(0, 1000) # compute a random value
	value2 = str(uuid.uuid4()) # generate a random unique id
	value3 = rand.random() # create a random value

	# Insert random values to the table
	curr.execute(
		"insert into dummy_metrics(timestamp, value1, value2, value3) values (%s, %s, %s, %s)",
		(datetime.datetime.now(pytz.timezone('Europe/London')), value1, value2, value3)
	)

# Main function
def main():
	prep_db() # prepare the database
	# Calculate last time the data was sent
	last_send = datetime.datetime.now() - datetime.timedelta(seconds = 10)
	# connection to the database
	with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
		# For each of 100  iterations
		for i in range(0, 100):
			# Use the cursor
			with conn.cursor() as curr:
				calculate_dummy_metrics_postgresql(curr) # add dummy metrics
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
	main() # run the main function