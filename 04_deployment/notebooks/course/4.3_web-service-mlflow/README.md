## Getting the model for deployment from MLflow
Starting the MLflow server with S3:

```bash
mlflow server \
    --backend-store-uri=sqlite:///mlflow.db \
    --default-artifact-root=s3://mlflow-models-maxim/ # can be a local address: mlflow-models
```

Downloading the artifact in case it was saved to an S3 bucket:

```bash
export MODEL_RUN_ID="1ca05c6d23f44066a4a4dcdbe1639de4"
export MLFLOW_TRACKING_URI="http://127.0.0.1:5000"

mlflow artifacts download \
    --run-id ${MODEL_RUN_ID} \
    --artifact-path model \
    --dst-path .
```