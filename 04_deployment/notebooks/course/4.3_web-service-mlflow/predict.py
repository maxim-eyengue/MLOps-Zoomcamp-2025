# Necessary import
import os
import mlflow
from flask import Flask, request, jsonify

# Get the experiment run ID
RUN_ID = os.getenv('RUN_ID')

# Get the model URI
logged_model = f's3://mlflow-models-alexey/1/{RUN_ID}/artifacts/model' # logged_model = f'runs:/{RUN_ID}/model'
# Load the model
model = mlflow.pyfunc.load_model(logged_model)

# Function for feature engineering
def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID']) # to concatenate integers
    features['trip_distance'] = ride['trip_distance']
    return features

# Function for making predictions
def predict(features):
    preds = model.predict(features) # making predictions
    return float(preds[0])


# Initialize the Flask app
app = Flask('duration-prediction')

# Predict endpoint: wraps the function for handling requests
@app.route('/predict', methods = ['POST']) # decorator for turning the function into an endpoint
def predict_endpoint():
    # Get the JSON data from the request
    ride = request.get_json()

    # Feature engineering of the data
    features = prepare_features(ride)
    # Make the predictions
    pred = predict(features)

    # Dictionary of results
    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    # return prediction
    return jsonify(result)

# If the script is executed
if __name__ == "__main__":
    # run the Flask application
    app.run(debug = True, host = '0.0.0.0', port = 9696)
