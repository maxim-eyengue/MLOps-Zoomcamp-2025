# Necessary import
import requests

# Ride information
ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 40
}
# Endpoint or webservice address
url = 'http://localhost:9696/predict'
# Get the response to our request
response = requests.post(url, json = ride)
# Print the resulting prediction
print(response.json())

# ---