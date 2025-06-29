# Necessary import
import os
import json
import boto3
import base64   
import mlflow

# Set a Kinesis client for handling data streams
kinesis_client = boto3.client('kinesis')

# Get the prediction stream name
PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')

# Get the experiment run ID
RUN_ID = os.getenv('MODEL_RUN_ID') # 1ca05c6d23f44066a4a4dcdbe1639de4

# Get the model URI
logged_model = f'mlflow-models/1/{RUN_ID}/artifacts/model' # local URI
# From MLFlow server: f'runs:/{RUN_ID}/model' 
# From S3 bucket: f's3://mlflow-models-maxim/1/{RUN_ID}/artifacts/model'

# Load the model
model = mlflow.pyfunc.load_model(logged_model)

# Check if it is a test run
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'

# Function for feature engineering
def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features

# Function for making predictions
def predict(features):
    pred = model.predict(features) 
    return float(pred[0])


# Lambda function
def lambda_handler(event, context):
    # print(json.dumps(event) - not necessary
    
    # Initialize the predictions event
    predictions_events = []
    
    # For each record in the sata stream
    for record in event['Records']:
        # Get the encoded data
        encoded_data = record['kinesis']['data']
        # Decode the data
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        # Load the data as json
        ride_event = json.loads(decoded_data)

        # print(ride_event) - not necessary
        # Get the ride input data (features)
        ride = ride_event['ride']
        # Get the ride id
        ride_id = ride_event['ride_id']
    
        # Prepare the data
        features = prepare_features(ride)
        # Make predictions
        prediction = predict(features)
    
        # Prediction event to output
        prediction_event = {
            'model': 'ride_duration_prediction_model',
            'version': '123',
            'prediction': {
                'ride_duration': prediction,
                'ride_id': ride_id   
            }
        }

        # If not a test
        if not TEST_RUN:
            kinesis_client.put_record(
                StreamName = PREDICTIONS_STREAM_NAME,
                Data = json.dumps(prediction_event),
                PartitionKey = str(ride_id)
            ) # Sending prediction events to the output stream
        
        # Add the prediction event to the list of predictions
        predictions_events.append(prediction_event)


    # return the predictions
    return {
        'predictions': predictions_events
    }

# ---