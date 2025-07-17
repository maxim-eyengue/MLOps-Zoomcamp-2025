# Necessary import
import json, requests 
from deepdiff import DeepDiff # to inform exactly 

# Event data
with open('event.json', 'rt', encoding='utf-8') as f_in:
    event = json.load(f_in)

# Address for making request
url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
# Send the request to trigger the lambda function and get the response
actual_response = requests.post(url, json = event).json()
print('actual response:')
print(json.dumps(actual_response, indent = 2))

# Expected response
expected_response = {
    'predictions': [
        {
            'model': 'ride_duration_prediction_model',
            'version': '1ca05c6d23f44066a4a4dcdbe1639de4',
            'prediction': {
                'ride_duration': 18.17,
                'ride_id': 256,
            },
        }
    ]
}

# Check the difference - specifying we only care about one sinificant digit after the dot
diff = DeepDiff(actual_response, expected_response, significant_digits = 1)
print(f'diff = {diff}')

# Check if significant differences in type and vales
assert 'type_changes' not in diff
assert 'values_changed' not in diff