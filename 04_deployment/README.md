![MLOps Zoomcamp](../images/banner-2025.jpg)

# 🚀 MLOps Zoomcamp – Week 4: Model Deployment
**Instructor:** Alexey Grigorev

---

## 📌 4.1 Three ways of deploying a model
**Model deployment** is part of the **operate** phase in MLOps, following **design**, where requirements are checked to make sure we need ML to solve our problem, and **training** phases, where models are trained and productionized into pipelines. The output of training is a model ready for deployment.

Deployment choices depend on prediction latency requirements: whether immediate predictions are needed or if predictions can be delayed by hours, days, or weeks. There are three primary deployment modes: batch/offline mode (predictions at regular intervals), online mode as a web service (model always available for immediate predictions), and streaming mode (model listens and reacts to event streams).

### Batch Mode Deployment

Batch mode applies the model periodically (e.g., every 10 minutes, hourly, daily, weekly) to new data pulled from a database, producing predictions saved back to a database or storage. Typically, a batch workflow is as follows: a scheduled job pulls recent data, runs the model, writes predictions, and downstream processes consume these predictions for actions like reporting or marketing campaigns. Churn prediction is a common use case in marketing: users likely to stop using a service are identified daily or weekly and targeted with incentives. Immediate prediction is unnecessary, making batch mode suitable.

### Web Service Deployment

Web service deployment hosts the model as a continuously running service accessible via HTTP requests, returning predictions immediately upon request. For example, a taxi app where the user requests ride duration prediction instantly before booking should be deployed through a web service as the model must be always available to provide immediate responses for user decisions. A web service involves a one-to-one client-server connection where the client sends a request, the service processes it, and returns a response while maintaining an active connection during processing.

### Streaming Mode Deployment

Streaming mode involves event-driven architecture with producers generating events and multiple independent consumers reading and reacting to these events asynchronously. Unlike web services, streaming uses a one-to-many or many-to-many relationship without explicit connections between producer and consumers: the producer pushes events without waiting for or knowing the consumers. Some Use cases include:
  - Taxi app where backend produces ride events consumed by multiple services independently (e.g., tip prediction, more accurate ride duration predictions).
  - Content moderation systems (e.g., YouTube) where video upload events trigger multiple moderation models for copyright, explicit content, hate speech, etc., with their predictions aggregated for final decisions like video removal.
  - Recommendation systems where new content events are consumed to update user recommendations dynamically.

#### Key Differences Between Deployment Modes

| Feature                | Batch Mode                       | Web Service                      | Streaming                        |
|------------------------|--------------------------------|---------------------------------|---------------------------------|
| Prediction Latency     | Delayed, periodic (minutes, days, etc.) | Immediate, on-demand             | Near real-time, event-driven     |
| Connectivity          | None during prediction run      | One-to-one, synchronous request | One-to-many or many-to-many, asynchronous events |
| Use Case Examples     | Churn prediction, marketing campaigns | Taxi ride duration prediction    | Tip prediction, content moderation, recommendations |
| Model Availability    | Runs only at scheduled times    | Always running                  | Always running, reacts to events |
| Consumer-Producer Relationship | Single batch job             | Single client-server             | Multiple independent consumers   |

As takeaway:
- Choose **batch mode** when immediate predictions are not critical and periodic updates suffice (e.g., churn detection, marketing).
- Choose **web service mode** when predictions must be available instantly to support real-time user decisions (e.g., taxi duration estimation).
- Choose **streaming mode** for event-driven systems requiring multiple independent reactions to data streams, supporting scalability and modularity (e.g., content moderation, multi-model prediction updates).

> **💡 Key Insight:** Deployment mode selection depends critically on prediction latency requirements and system architecture, balancing immediacy, scalability, and complexity to best fit the ML use case.  
                       

## 🛠️ 4.2 Web-services: Deploying models with Flask and Docker

We will now focus on deploying a machine learning model saved as a pickle file into a web service using Flask and Docker. This will be done by creating a virtual environment, scripting the model, wrapping it in a Flask app, and finally containerizing the application with Docker.

#### Environment Setup and Version Management
It is crucial to match the exact version of scikit-learn used to create the pickle file to avoid incompatibility issues during unpickling; this is verified using `pip freeze | grep scikit-learn` or `pip list | grep scikit-learn`. We can then install the specific version in the virtual environment along with other necessary libraries specifyikng the version of Python that we want to use: `pipenv install scikit-learn==1.0.2 flask --python=3.9`. Note, we are using Python 3.9 for the course. A virtual environment is useful as it isolates dependencies specific to this project, avoiding conflicts with global Python packages. When using `Pipenv` for creating virtual environments, dependency versions are pinned in [`Pipfile`](./notebooks/course/4.2_web-service/Pipfile) and [`Pipfile.lock`](./notebooks/course/4.2_web-service/Pipfile.lock) to ensure reproducible environments across installations.

#### Building the Flask Web Service
First we create the model prediction logic in Python. For this purpose, we create a [predict.py](./notebooks/course/4.2_web-service/predict.py) script to:
  - Load the model and dictionary vectorizer from the pickle file using `pickle.load`.
  - Perform feature engineering as done during model training (e.g., concatenating pickup and dropoff IDs as a new feature).
  - Transform features and generates predictions using the loaded model.
Testing will be done with a [`test.py`](./notebooks/course/4.2_web-service/test.py) script that imports the prediction functions and prints the output for sample ride data, verifying correctness before deployment.

The Flask application wraps the prediction logic to create an HTTP endpoint:
  - Imports `Flask`, `request`, and `jsonify` to handle incoming JSON requests and return JSON responses.
  - Defines a route with a decorator that makes the prediction function accessible via HTTP POST requests to `/predict`.
  - Runs locally on port 9696 for development testing.
Note that **Flask's built-in server** is intended only for **development**. This said, launching the Flask app with `python predict.py` will raise a warning that advises using a production-grade Web Server Gateway Interface (WSGI) server like **Gunicorn** for deployment: 
```sh
gunicorn --bind=0.0.0.0:9696 predict:app
```
For testing: `python test.py`.

> NB: The `requests` library is installed as a development dependency only: `pipenv install --dev requests`, since it is required for testing but not for serving the app in production.

#### Dockerizing the Application
We can create A [Dockerfile](./notebooks/course/4.2_web-service/Dockerfile) to containerize the Flask application. It will:
  - Use a Python 3.9 slim base image to ensure consistency with the development environment.
    > Available Python docker images can be found [here](https://hub.docker.com/_/python).
  - Update pip to the latest version to avoid issues with package installations (e.g., for packages like xgboost).
  - Copy `Pipfile` and `Pipfile.lock` into the container and installs dependencies directly into the system Python environment (**no virtual environment inside Docker**). The ``--system`` and `--deploy` flags in the pipenv install command in the Dockerfile are used to install dependencies system-wide (skipping environment creation).
  - Copy the model pickle file and the Flask app script into the container's working directory.
  - Set the container to expose port 9696 (open the port in the container) and run the app using Gunicorn, by specifying the Flask app module and app variable for Gunicorn to serve.

To build the docker image, run it and test our web service, check the [instructions](./notebooks/course/4.2_web-service/README.md). With the Docker container ready, the model can be deployed on any infrastructure supporting Docker, such as AWS Elastic Beanstalk or Kubernetes.

> **ℹ️ Note:** Ensuring feature engineering in the serving code exactly matches training is critical for consistent predictions. 

> **ℹ️ Note:** Flask's built-in server is not suitable for production due to performance and security limitations; Gunicorn or similar WSGI servers are recommended for production deployments.

> **ℹ️ Note:** Installing testing dependencies like `requests` as development dependencies keeps production environments clean and minimal, avoiding unnecessary packages in deployed containers.

## 📉 4.3 Web-services: Getting the models from the model registry (MLflow)
Previously, a linear regression model was deployed as a web service using Flask with functions to prepare features and make predictions, and exposed as an endpoint for querying predictions. We now need to integrate this deployment with the MLflow model registry to retrieve models either by production stage or by specific run ID. For that we will use a random forest model.
Note that we will be running `MLFlow`:
```sh
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root=mlflow-models # can be adjusted to specify a remote s3 bucket address: s3://mlflow-models-maxim 
```
Using a [notebook](./notebooks/course/4.3_web-service-mlflow/random-forest.ipynb), models and related artifacts (dictionary vectorizer, model parameters) will be logged and tracked in MLflow runs, allowing retrieval by run ID for deployment purposes. The model registry supports promoting models to production stages but using run IDs ensures exact version control in deployments.

Note that the Flask environment should be configured to include MLflow and dependencies with a [pipfile](./notebooks/course/4.3_web-service-mlflow/Pipfile), ensuring proper package installation for running the prediction service. Setting the MLflow tracking URI correctly is critical for accessing the model registry and artifacts; misconfiguration leads to errors in loading models.

While logging the model and the vectorizer in our [notebook](./notebooks/course/4.3_web-service-mlflow/random-forest.ipynb), it is good practtice to wrap them in a **pipeline** using `sklearn.pipeline.make_pipeline`. Combining the dictionary vectorizer and the random forest regressor into one pipeline object which is then logged and retrieved as a single model artifact simplifies artifact management and model deployment.

In our Flask application, it is also recommended to return **model versioning** in the response. Including the model run ID (version) in the prediction response payload provides traceability of which model version generated each prediction, aiding in debugging and auditing.

Relying on the MLflow tracking server at runtime can cause deployment failures if the server is down, especially when scaling new model instances that need to connect to it. A better approach is to bypass the tracking server by directly fetching models from the artifact storage (e.g., S3, mlflow-models folder) using the full artifact URI, removing dependency on the MLflow tracking server during prediction serving.

Model run ID and other information can be configured via environment variables, enabling flexible deployment setups such as Kubernetes where model versions can be updated by changing environment variables without code changes. Note that some [instructions](./notebooks/course/4.3_web-service-mlflow/README.md) are available in case we use an S3 bucket. The most important we will need in our case is saving the run id:
```sh
export MODEL_RUN_ID="1ca05c6d23f44066a4a4dcdbe1639de4"
```
This flexibility allows seamless integration with containerized deployments and orchestration platforms, supporting dynamic model version updates and scalable serving architectures. We can then test our [Flask application](./notebooks/course/4.3_web-service-mlflow/predict.py) by running it: `python predict.py` and [testing](./notebooks/course/4.3_web-service-mlflow/test.py) it in a different window: `python test.py`. Once done, we can dockerized the application as already done earlier.

> **💡 Key Insight:** Combining feature transformation and model into a single pipeline artifact simplifies deployment by reducing artifact management complexity and improves code maintainability. Direct artifact URI usage removes runtime dependencies on the tracking server, enhancing reliability and scalability of model serving.  

> **❗ Important:** Always include model version information in prediction responses for effective model management and traceability in production systems.  

> **ℹ️ Note:** Environment variable configuration for model identifiers supports flexible and scalable deployment strategies such as Kubernetes.  
                            

## 🖥️ 4.4 Streaming: Deploying models with Kinesis and Lambda  
AWS Kinesis is an event streaming service, similar to Kafka or other message brokers, used to send and read events in real time; AWS Lambda functions can consume events from Kinesis streams to process data without managing servers.

We will create a Kinesis stream, configuring a Lambda function to consume from that stream, and embedding a machine learning model inside the Lambda for real-time predictions on streaming data. This approach contrasts with prior methods deploying models as web services; here, the Lambda reacts to streaming events for immediate inference, useful for scenarios like updating ride duration predictions as rides progress using a more accurate model than the previous one already deployed.

> [AWS Lambda Notes from the ML Zoomcamp](https://github.com/maxim-eyengue/Python-Codes/blob/main/ML_Zoomcamp_2024/09_serverless/Summary_Session_09.md)

> [Tutorial: Using Amazon Lambda with Amazon Kinesis](https://docs.amazonaws.cn/en_us/lambda/latest/dg/with-kinesis-example.html)


#### AWS Lambda Fundamentals and Role Configuration
Lambda enables running code without managing servers or infrastructure. You write code that AWS executes in response to triggers like Kinesis events. To allow Lambda to read from Kinesis, an IAM role with specific permissions (e.g., read records from Kinesis streams) must be created and attached to the Lambda function. These permissions include access to shards (partitions of the stream) and logs. Execution roles need fine-grained policies restricting Lambda’s access only to necessary services and resources, improving security and governance. The predefine permission policies that we will need are accessible with the `AWSLambdaKinesisExecutionRole`.

#### Creating and Testing Lambda Functions with Kinesis Triggers
Lambda functions can be written in Python, with event payloads representing Kinesis records; initial tests involve printing events to CloudWatch logs to verify the Lambda is triggered correctly. Events from Kinesis arrive as batches of records encoded in base64; decoding these is necessary to extract the original payload, often JSON-formatted data representing domain-specific events (e.g., ride information). Testing involves sending sample events to the Kinesis stream and observing Lambda’s processing and logging behavior, ensuring correct decoding and handling of multiple records per invocation.

We will create a Lambda function using the AWS UI and specifying the role created earlier. We will also test the function using a new event. Because streaming is asynchronous and decoupled, each event needs a unique identifier to correlate input events with their predictions or outputs later. For that, we will add an ID (e.g., ride_id) as part of the results from the handler of our [lambda function](./notebooks/course/4.4_streaming/lambda_function.py).

Instead of returning predictions directly (as in synchronous web services), Lambda writes prediction results to a separate Kinesis stream; this requires additional permissions for Lambda to put records into the output stream. Output events include metadata such as model name and version to track which model produced the prediction, important when multiple consumers or models exist in the streaming architecture. Note that we will have to create a Kinesis Data stream (named `ride_events`) on provisioned mode (data stream capavity is fixed vs on-demand). We will only set one shard as there won't be a lot of requests. Shards are paid hourly. In the Lambda function we will set the Kinesis Data stream as trigger.

> Ps: Make sure to attach the policy permissions  to the IAM role used.

#### Using AWS SDK (boto3) for Kinesis Interaction
The Python `boto3` library is used within Lambda to interact with Kinesis streams programmatically, sending prediction events to the output stream using `put_record` or batch operations like `put_records` for efficiency via a kinesis boto3 client. Proper error handling and IAM permissions are critical to ensure Lambda can write to Kinesis without access denials. We will create a new policy for that and attah it to the role set earlier.

#### Reading from Kinesis Streams Outside Lambda
The AWS CLI can be used to read records from a Kinesis stream, involving obtaining a shard iterator and fetching records; this is useful for debugging or consuming stream data outside Lambda functions. Stream records are base64 encoded and require decoding to reveal the original JSON payload representing prediction results or other data. This should be done in the Lambda function and also in the CLI. After sending the data event to the lambda function, we can check its logs to understand what happened.

> Here are some [instructions](./notebooks/course/4.4_streaming/README.md) for the various interaction between Kinesis and Lambda using the CLI. 

> We can use `jq` for formatting json result in the CLI: `echo $RESULT | jq` and access data too. To install this tool: `brew install jq`.

> NB: Our [lambda function](./notebooks/course/4.4_streaming/lambda_function.py) can be tested locally using a python [script](./notebooks/course/4.4_streaming/test.py):
```sh
# Manage environment variables for the lambda function
export PREDICTIONS_STREAM_NAME="ride_predictions"
export MODEL_RUN_ID="1ca05c6d23f44066a4a4dcdbe1639de4"
export TEST_RUN="True"

# Run the test
python test.py
```


#### Packaging and deploying Lambda with Machine Learning Models Using Docker
To include complex dependencies and machine learning models (e.g., MLflow pipelines), Lambda functions can be packaged as container images using [Docker](./notebooks/course/4.4_streaming/Dockerfile), enabling consistent [environments](./notebooks/course/4.4_streaming/Pipfile) and easier dependency management. AWS provides [base Docker images](https://gallery.ecr.aws/lambda/python) for Lambda functions with Python runtimes; these images can be extended by installing necessary Python packages (mlflow, scikit-learn, boto3) and copying the Lambda code and model files. The [Docker image](./notebooks/course/4.4_streaming/Dockerfile) must specify the Lambda handler function as the entry point, following AWS Lambda container image conventions.

> NB: In our predictions result, it is goood practice to specify the model used with its version along with the event id and the predicted value.

After building the Docker image locally or on a remote instance, the image is pushed to **AWS Elastic Container Registry (ECR)**, a managed Docker container registry service, for deployment to Lambda. Lambda functions can be created or updated to use container images by specifying the ECR image URI and configuring environment variables such as prediction stream names and model run IDs. Proper IAM roles must be updated to grant Lambda access to required services including Kinesis streams and S3 buckets storing model artifacts.

> Reminder: [Instructions](./notebooks/course/4.4_streaming/README.md) on how to build and run the docker container are available. It will either work on a remote instance with an instance profile (a way of giving permission to an EC2 instance without providing access keys), or locally (need to specify access keys).

> Important: We copied the [mlflow models folder](./notebooks/course/4.4_streaming/mlflow-models/) in the docker image with: `COPY [ "mlflow-models", "./" ]` as we did not save the model to a remote s3 bucket. To test the docker image, we can use a [script](./notebooks/course/4.4_streaming/test_docker.py).

#### Performance Tuning and Lambda Configuration
Lambda memory and timeout settings affect function performance and cost; increasing memory can speed up execution but also increases cost proportionally. Initial invocations may be slower due to cold starts and model loading; subsequent invocations benefit from caching and are faster.

#### Summary of Key Steps and Concepts
| Step                          | Description                                                                                                   |
|-------------------------------|---------------------------------------------------------------------------------------------------------------|
| Create IAM Role               | Define execution role with permissions for Kinesis and S3 access                                              |
| Create Kinesis Streams        | Input stream for events and output stream for predictions                                                     |
| Develop Lambda Function       | Consume input stream events, decode, apply ML model, write predictions to output stream                        |
| Test Lambda Locally           | Use event payloads to simulate Kinesis events                                                                 |
| Package with Docker           | Build container image with dependencies and model                                                             |
| Push to AWS ECR              | Upload container image for Lambda use                                                                          |
| Deploy Lambda with Container | Create Lambda function using container image and configure environment variables                               |
| Monitor and Tune              | Use CloudWatch logs for debugging and adjust memory/timeouts for optimal performance                           |

#### Important Clarifications and Insights
> **AWS Lambda**’s main promise is running code **without managing servers**; you only care that your code executes in response to events, abstracting away infrastructure details.
> Streaming architectures require careful **event correlation via unique IDs** because responses are not synchronous as with traditional request-response web services. 
> **Decoding base64 payloads** and **handling batches** of records are essential when processing Kinesis events in Lambda. 
> **IAM roles and permissions** must be carefully crafted to allow Lambda to read from and write to specific Kinesis streams and access S3 model artifacts securely.  
> **Packaging ML models** into **Lambda** via **Docker** containers simplifies dependency management and ensures consistent runtime environments.    
> We can crate a **lambda function** based on a **docker image**. Using the **ECR** simplifies the process.     
> **Cost considerations:** Each Kinesis shard costs money per hour, and Lambda memory size affects invocation cost; always balance resource allocation with budget and performance needs.  
  

## 🧰 4.5 Batch: Preparing a scoring script
Batch deployment involves applying a trained model offline to a batch of data, differing from online mode where a model is deployed as a web service handling real-time requests. Batch deployment is useful for analytical purposes such as evaluating deviations between actual and predicted values over a dataset. The example use case is not an ideal one: we will predict taxi ride durations and analyze the difference between actual and predicted durations to detect patterns like traffic jams. We will turn a [training notebook](./notebooks/course/4.3_web-service-mlflow/random-forest.ipynb) into a [scoring notebook](./notebooks/course/4.5_batch/score.ipynb) that applies the trained model instead of just training it.

Since the dataset lacks a natural unique ride ID, universally unique identifiers (UUIDs) are generated for each row to uniquely identify rides. This is done in Python using the built-in `uuid` library, specifically with `uuid4`. These UUIDs are added as a new column to the DataFrame, allowing predictions to be linked back to individual rides.

#### Parameterizing Input and Output

- The script is parameterized to accept input and output file paths, allowing flexible specification of data sources and destinations. Input files can be URLs, enabling direct download and reading by pandas without manual download steps   .
- Further parameters include year, month, and taxi type, enabling the script to dynamically construct file paths based on these inputs using formatted strings (f-strings) with zero-padding for months   .
- Output directories are organized by taxi type and time period, enhancing file management for batch results  .

#### Refactoring into Functions

- Code is organized into functions such as `generate_uuids` for UUID creation and `apply_model` for the main scoring logic, which takes parameters like input file, model version, and output file path    .
- Model versioning is included by passing the MLflow run ID (or model version) to the scoring function, and this version is stored with each prediction to track which model produced the results   .
- The code avoids global variables, encapsulating logic within functions and enabling easier testing and maintenance  .

#### Testing and Running the Script

- The script can be executed multiple times with different parameters (e.g., for different months) to generate batch predictions for various data slices  .
- To avoid manual interaction with notebooks, the notebook is converted into a standalone Python script using `jupyter nbconvert --to script`   .
- The script is further enhanced by adding a `run` function and using the `if __name__ == "__main__":` guard to allow command-line execution with parameters for taxi type, year, and month   .
- Command-line parameters are accessed via `sys.argv` for simplicity, though more robust options like `argparse` or `click` are recommended for production use     .
- Basic logging via print statements is added to track progress through reading data, loading the model, applying the model, and saving results, improving usability and debugging   .

#### Dependencies and Packaging

- Required Python libraries include `pandas`, `pyarrow` or `fastparquet` for Parquet file handling, `mlflow` for model management, `scikit-learn` for model prediction, `boto3` for S3 access, and `uuid` (built-in)   .
- The script can be packaged in a Docker container with all dependencies specified to ensure reproducibility and ease of deployment across environments  .
- For full batch deployment, the script can be scheduled and run on cloud services such as AWS Batch, ECS, or Kubernetes jobs, enabling automated, scalable batch scoring pipelines  .

---

> **💡 Key Insight:** Batch deployment scripts should be self-contained, parameterized, and organized into functions to facilitate automation, reproducibility, and scalability in MLOps workflows.
   

## 🧭 4.6 Batch scoring with an orchestrator
To do it:
- Connect to MLFlow.
- Create a transformation block.
- Get the model from the registry, and apply it.

## 📝 4.7 Homework
Homework for this module is available [here.](notebooks/homework/homework_04.ipynb).

---
