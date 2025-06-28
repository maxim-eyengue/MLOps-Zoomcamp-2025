# Necessary import
import pickle
from flask import Flask, request, jsonify

# Load the one-hot encoder and the predictive model
with open('lin_reg.bin', 'rb') as f_in:
    (dv, model) = pickle.load(f_in)

# Function for feature engineering
def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID']) # to concatenate integers
    features['trip_distance'] = ride['trip_distance']
    return features

# Function for making predictions
def predict(features):
    X = dv.transform(features) # one-hot encoding
    preds = model.predict(X) # making predictions
    return float(preds[0])

# Initialize the Flask app
app = Flask('duration-prediction')

# Predict endpoint: Function wrapper for handling requests
@app.route('/predict', methods = ['POST']) # decorator for turning the function into an endpoint
def predict_endpoint():
    # Get the json data from the request
    ride = request.get_json()

    # Prepare features
    features = prepare_features(ride)
    # Make predictions
    pred = predict(features)

    # Dictionary with results
    result = {
        'duration': pred
    }

    # return a json object conaining the prediction
    return jsonify(result)

# If the scripyt is executed
if __name__ == "__main__":
    # run the flask application
    app.run(debug = True, host = '0.0.0.0', port = 9696)