# Necessary import
from pathlib import Path

import model


def read_text(file):
    "Read a testing file."
    # Get the directory of the testing file
    test_directory = Path(__file__).parent

    # Read the file
    with open(test_directory / file, 'rt', encoding='utf-8') as f_in:
        return f_in.read().strip()


def test_base64_decode():
    "Test the `decode` function."
    base64_input = read_text('data.b64')  # reading the input file

    actual_result = model.base64_decode(base64_input)  # decoding the file
    expected_result = {
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66,
        },
        "ride_id": 256,
    }

    # Checking the match
    assert actual_result == expected_result


def test_prepare_features():
    "Test the model's method that prepares features."
    model_service = model.ModelService(None)

    ride = {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66,
    }  # input

    actual_features = model_service.prepare_features(ride)

    expected_fetures = {
        "PU_DO": "130_205",
        "trip_distance": 3.66,
    }

    # Check that the match is coorect
    assert actual_features == expected_fetures


# Class for declaring a mock model
class ModelMock:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


def test_predict():
    "Test the model predict method."
    model_mock = ModelMock(10.0)  # declaring a mock model
    model_service = model.ModelService(model_mock)  # passing it for model serving

    features = {
        "PU_DO": "130_205",
        "trip_distance": 3.66,
    }

    actual_prediction = model_service.predict(features)  # get the mock prediction
    expected_prediction = 10.0

    assert actual_prediction == expected_prediction  # check the match


def test_lambda_handler():
    "Test the lambda handler."
    model_mock = ModelMock(10.0)
    model_version = 'Test123'
    model_service = model.ModelService(model_mock, model_version)

    base64_input = read_text('data.b64')

    event = {
        "Records": [
            {
                "kinesis": {
                    "data": base64_input,
                },
            }
        ]
    }

    actual_predictions = model_service.lambda_handler(event)
    expected_predictions = {
        'predictions': [
            {
                'model': 'ride_duration_prediction_model',
                'version': model_version,
                'prediction': {
                    'ride_duration': 10.0,
                    'ride_id': 256,
                },
            }
        ]
    }

    assert actual_predictions == expected_predictions
