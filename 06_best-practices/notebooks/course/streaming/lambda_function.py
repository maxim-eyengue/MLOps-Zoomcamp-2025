# Necessary import
import os

import model

# Get the prediction stream name
PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')
# Get the experiment run ID
RUN_ID = os.getenv('MODEL_RUN_ID', '1ca05c6d23f44066a4a4dcdbe1639de4')
# Check if it is a test run
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'


# Initialization for model serving
model_service = model.init(
    prediction_stream_name=PREDICTIONS_STREAM_NAME, run_id=RUN_ID, test_run=TEST_RUN
)


# Lambda function
def lambda_handler(event, context):
    # pylint: disable=unused-argument
    # serve the model
    return model_service.lambda_handler(event)


# ---
