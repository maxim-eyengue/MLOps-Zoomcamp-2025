#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Necessary import
import pickle
import pandas as pd

# Python version
get_ipython().system('python -V')


# In[2]:


# Check sci-kit learn version
get_ipython().system('pip freeze | grep scikit-learn # pip list | grep scikit-learn')


# In[3]:


# Open the model file
with open('model.bin', 'rb') as f_in:
    # Load the encoder and the model
    dv, model = pickle.load(f_in)


# If any warnings, we should make sure to install the version of scikit-learn used to saved the model:
# ```sh
# pip install scikit-learn==1.5.0
# ```

# In[4]:


# Set of categrical features
categorical = ['PULocationID', 'DOLocationID']

# Function for reading the data
def read_data(filename):
    # Read the parquet file
    df = pd.read_parquet(filename)
    
    # # Feature engineering for creating the duration column
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    # Convert durations into minutes
    df.duration = df.duration.dt.total_seconds() / 60

    # Filtering for trips lasting from 1 min to 1 hour
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    # Fill missing values and conert data type
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    # Return the dataframe
    return df


# In[5]:


# Set the date
year, month = 2023, 3

# Read the Yellow taxi data
df = read_data(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet')


# In[6]:


# Get the validation data dictionaries
dicts = df[categorical].to_dict(orient = 'records')
# Encode validation data
X_val = dv.transform(dicts)
# Make predictions
y_pred = model.predict(X_val)


# In[7]:


# Predictions standard deviation
print(f"Predictions Standard Deviation: {round(y_pred.std(), 2)}")


# In[8]:


# Let's create an artificial `ride_id` column
df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')


# In[ ]:


# Let's write the `ride_id` and `predictions`
df_result = df[['ride_id']].copy()
df_result["duration"] = y_pred 

# First lines
df_result.head()


# In[11]:


# Address to save the data
output_file = f"predictions_{year:04d}_{month:02d}.parquet"
# Saving the data to parquet
df_result.to_parquet(
    output_file,
    engine = 'pyarrow',
    compression = None,
    index = False
)


# ---
