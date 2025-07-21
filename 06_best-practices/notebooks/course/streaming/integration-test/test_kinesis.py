# pylint: disable=duplicate-code

# Necessary import
import os
import json
from pprint import pprint

import boto3
from deepdiff import DeepDiff

# Create Kinesis endpoint and client for local testing
kinesis_endpoint = os.getenv('KINESIS_ENDPOINT_URL', "http://localhost:4566")
kinesis_client = boto3.client('kinesis', endpoint_url = kinesis_endpoint)

# Set the stream-name and an id for the shard
stream_name = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')
shard_id = 'shardId-000000000000'

# Get the shard iterator
shard_iterator_response = kinesis_client.get_shard_iterator(
    StreamName = stream_name,
    ShardId = shard_id,
    ShardIteratorType = 'TRIM_HORIZON',
)
# Get the shard iterator id
shard_iterator_id = shard_iterator_response['ShardIterator']

# Retrieve records from the shard
records_response = kinesis_client.get_records(
    ShardIterator = shard_iterator_id,
    Limit = 1
)
# Get and print the records
records = records_response['Records']
pprint(records)

# Assert it is only one record
assert len(records) == 1

# Load / decode the data
actual_record = json.loads(records[0]['Data'])
pprint(actual_record) 

# Actual record
expected_record = {
    'model': 'ride_duration_prediction_model',
    'version': '1ca05c6d23f44066a4a4dcdbe1639de4', # Test7 to get an error
    'prediction': {
        'ride_duration': 18.17, # 21.3 to get an error
        'ride_id': 256,
    },
}

# Check if any differences
diff = DeepDiff(actual_record, expected_record, significant_digits = 1)
print(f'diff={diff}')

# Assert match
assert 'values_changed' not in diff
assert 'type_changes' not in diff

# Confirm everything is okay
print('all good')
