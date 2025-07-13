# Necessary import
import os
import json
import boto3
import base64   
import mlflow


# Function to get the model from its location
def get_model_location(run_id):
    # Get the model location via the environments variable
    model_location = os.getenv('MODEL_LOCATION')
    # Locally: MODEL_LOCATION='mlflow-models/1/1ca05c6d23f44066a4a4dcdbe1639de4/artifacts/model'
    # From MLFlow server: MODEL_LOCATION='runs:/1ca05c6d23f44066a4a4dcdbe1639de4/model' 

    # If the model location is provided via terminal
    if model_location is not None:
        return model_location # to return the model location

    # Build the model location locally or from an s3 bucket
    model_bucket = os.getenv('MODEL_BUCKET', 'mlflow-models') # For S3: 'mlflow-models-maxim'
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID', '1')

    # Model location from local bucket
    model_location = f'{model_bucket}/{experiment_id}/{run_id}/artifacts/model' # For s3: add `s3://` at the beggining of the f string.
    return model_location

# Function to load the model
def load_model(run_id):
    # Get the model location
    model_path = get_model_location(run_id)
    # Load the model
    model = mlflow.pyfunc.load_model(model_path)
    return model

# function to decode encoded data (for stream data)
def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    ride_event = json.loads(decoded_data) # Load the data as json file
    return ride_event


# Define a class for model serving
class ModelService:
    def __init__(self, model, model_version = None, callbacks = None):
        self.model = model
        self.model_version = model_version
        self.callbacks = callbacks or []

    # Method for feature engineering
    def prepare_features(self, ride):
        features = {}
        features['PU_DO'] = f"{ride['PULocationID']}_{ride['DOLocationID']}" # '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
        features['trip_distance'] = ride['trip_distance']
        return features
    
    # Method for making predictions
    def predict(self, features):
        pred = self.model.predict(features) 
        return float(pred[0])

    # Lambda Method
    def lambda_handler(self, event):        
        # Initialize the predictions event
        predictions_events = []
        
        # For each record in the sata stream
        for record in event['Records']:
            # Get the encoded data
            encoded_data = record['kinesis']['data']
            # Decode the data
            ride_event = base64_decode(encoded_data)

            # Get the ride input data (features)
            ride = ride_event['ride']
            # Get the ride id
            ride_id = ride_event['ride_id']
        
            # Prepare the data
            features = self.prepare_features(ride)
            # Make predictions
            prediction = self.predict(features)
        
            # Prediction event to output
            prediction_event = {
                'model': 'ride_duration_prediction_model',
                'version': self.model_version,
                'prediction': {
                    'ride_duration': prediction,
                    'ride_id': ride_id   
                }
            }

            # Callbacks for deploying the model with kinesis
            for callback in self.callbacks:
                callback(prediction_event)
            
            # Add the prediction event to the list of predictions
            predictions_events.append(prediction_event)

        # return the predictions
        return {
            'predictions': predictions_events
        }


# Class for building a Kinesis callback
class KinesisCallback:
    # Initialization Method
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    # Method for sending prediction events to the output stream
    def put_record(self, prediction_event):
        ride_id = prediction_event['prediction']['ride_id']

        self.kinesis_client.put_record(
            StreamName = self.prediction_stream_name,
            Data = json.dumps(prediction_event),
            PartitionKey = str(ride_id),
        )


# Function to create a kinesis client
def create_kinesis_client():
    # Get the endpoint url via environment variables
    endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')

    if endpoint_url is None: # if no endpoint
        return boto3.client('kinesis') # return a kinesis client

    # Return a Kinesis client with with an endpoint
    return boto3.client('kinesis', endpoint_url = endpoint_url)


# Function to initialize the model for model serving
def init(prediction_stream_name: str, run_id: str, test_run: bool):
    # Load the model
    model = load_model(run_id)

    # Initialize callbacks
    callbacks = []

    # If this run is not a simple test
    if not test_run:
        # Create a Kinesis client
        kinesis_client = create_kinesis_client()
        # Create a Kinesis callback for sending data into streams
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        # Add the callback to the model set of callbacks
        callbacks.append(kinesis_callback.put_record)

    # Initialize the model
    model_service = ModelService(model = model, model_version = run_id, callbacks = callbacks)

    # Return the model onject for serving
    return model_service

# ---