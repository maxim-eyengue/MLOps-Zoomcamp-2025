# 🛠️  Set-up & Use MLflow Locally

Getting started with MLflow locally is straightforward. You'll need to have Python and `pip` installed on your system.

## Installation

The first step is to install the MLflow package using `pip`. It's a good practice to do this within a virtual environment to avoid potential conflicts.

```sh
pip install mlflow
```

To verify the installation and check the version, run:

```sh
mlflow --version
```

To get help with the MLflow command-line interface, run:
```sh
mlflow --help
```

## Starting the Tracking UI

When there is no need of storing information on a remote server, you can simply use MLflow's built-in user interface (UI). It is a powerful tool for visualizing and comparing your experiment runs locally. 

To start the MLflow Tracking UI, open your terminal and run:
```sh
mlflow ui
```

By default, this will start a server on your local machine at `http://127.0.0.1:5000`. When you run an experiment, MLflow will create a directory called `mlruns` in your current working directory to store all information about your runs, including experiment data.

For more advanced use cases, you can specify a backend store URI (postgressql, mysql, sqlite or mssql). For example, to use a local SQLite database to store your experiment metadata (metrics, parameters, tags), you can start the UI by running:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db 
```

This will create a file named `mlflow.db` in your current directory, that will serve as backend.

> ⚠️ Note: Some backend is necessary to get access to the model registry.

## Run the MLflow Tracking Server
For more robust use cases, especially for team collaboration or moving toward production, it is better to launch a tracking server instead:
```sh
mlflow server --backend-store-uri sqlite:///backend.db --default-artifact-root ./artifacts_local
```
You can also define a backend store for saving run information (metrics, parameters, tags), and an artifacts store for models and environments requirements, and specify a host address (e.g., `--host 127.0.0.1`) and even a port (e.g., `--port 8080`).

> NB: `mlflow server` allows remote backends and cloud artifact storage, so your team can collaborate from different machines. Also note that it is available through **Databricks** for example, with the Experiments User Interface.


## Logging Experiments

Here's a basic example of how to use MLflow in your Python script to track a simple machine learning model.

```python
# Necessary import
import mlflow # Experiment tracking
from mlflow.tracking import MlflowClient # For interacting with the model registry
from sklearn.datasets import load_iris # Data
from sklearn.linear_model import LogisticRegression # Model
from sklearn.metrics import accuracy_score # Metrics

## Set the tracking URI as local server (in case you are using a server)
mlflow.set_tracking_uri("http://127.0.0.1:5000")
## If launching the User Interface instead, specify the tracking URI as your backend store if you have one
# ---> mlflow.set_tracking_uri("sqlite:///mlflow.db")
## If you don't have any:
# ---> it will by default be the `mlruns` folder in your current working directory


# List experiments
mlflow.search_experiments()

# Set a Machine Learning experiment
mlflow.set_experiment("my-first-experiment") # If not mlflow will use the default one
# If the experiment set doesn't exist it will be created automatically

# Start an experiment run 
with mlflow.start_run():
    # Load the iris data set features and target
    X, y = load_iris(return_X_y = True)

    # Model parameters
    params = {
        "C": 0.1,
        "random_state": 42
    }
    # Log the model parameters
    mlflow.log_params(params)

    # Initialize and train the logistic model
    lr = LogisticRegression(**params).fit(X, y)
    # Make predictions
    y_pred = lr.predict(X)
    # Log the model accuracy
    mlflow.log_metric("accuracy", accuracy_score(y, y_pred))

    # Log the model
    mlflow.sklearn.log_model(lr, artifact_path = "models")
    # Check the mlfow artifact uri
    print(f"default artifacts URI: '{mlflow.get_artifact_uri()}'")

# Show the updated lists of experiments
mlflow.search_experiments()

# Create an mlflow client
client = MlflowClient(tracking_uri = "http://127.0.0.1:5000")

# Get the id of the first experiment run
# It is possible to filer to specific runs by some criteria (e.g., run start time, status, tags, metrics values, etc.)
run_id = client.search_runs(experiment_ids = '1')[0].info.run_id
# Model name
model_name = 'iris-classifier'
# Register the model
mlflow.register_model(
    model_uri = f"runs:/{run_id}/models", 
    name = model_name
)

# Model version
model_version = 1 # The version increases each time we registered the same model and should be adjusted accordingly
# Model alias
alias = "challenger" # models can for example go from `challenger` (new) to `champion` (in production)

# Assign alias to the model
client.set_registered_model_alias(
    name = model_name,
    alias = alias,
    version = model_version
)

# Model URI for logging:
# With model version: f"models:/{model_name}/{model_version}"`
# With aliasing: f"models:/{model_name}@{alias}"
logged_model_uri = f"models:/{model_name}@{alias}"


# Model transitioning consists of copying models and re-aliasing
# New model name for production
prod_model_name = "iris-clas-prod"
# Copy the challenger model for creating a production model
client.copy_model_version(src_model_uri = logged_model_uri, dst_name = prod_model_name)
# Alias the model for production
client.set_registered_model_alias(
    name = prod_model_name,
    alias = "champion",
    version = model_version
)

# Update model URI
logged_model_uri = f"models:/{prod_model_name}@champion"

# Load the model as a python function using its URI
model = mlflow.pyfunc.load_model(logged_model_uri)
# Make a prediction
y_pred = model.predict(X)
# Model score
print(accuracy_score(y, y_pred))
```

### How It Works

* **`mlflow.start_run()`**: Creates a new MLflow run. All the tracking for this experiment will be recorded under this run.
* **`mlflow.log_params()`**: Takes a dictionary of parameters and logs them for the current run. This is useful for keeping track of the hyper-parameters you used.
* **`mlflow.log_metric()`**: Logs a single key-value metric. You can call this multiple times to log different metrics.
* **`mlflow.sklearn.log_model()`**: Logs your trained scikit-learn model as an artifact. MLflow has integrations for many other popular machine learning libraries as well.

### Viewing Your Experiments

After running your script, refresh the MLflow UI in your browser (`http://127.0.0.1:5000`). You will see your new run listed. Click on it to see the detailed view, which includes the parameters you logged, the accuracy metric, and the saved model artifact. This interface allows you to compare different runs, which is incredibly useful when you are tuning your models. 

> ⚠️ NB: Model staging now works with aliases and tags. For example, you can assign aliases like **challenger** to newly trained models and **champion** to production-ready ones.  Aliasing can also be managed directly from the UI. Some code is even available to upload and use registered models.

## For More...
- [MLFlow Official Documentation](https://www.mlflow.org/docs/latest/index.html)
