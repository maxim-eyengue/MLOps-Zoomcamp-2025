![MLOps Zoomcamp](../images/banner-2025.jpg)

# 🚀 MLOps Zoomcamp – Week 2: Experiment tracking and model management

**Instructor:** Cristian Martinez

---

## 📌 2.1 Experiment tracking introduction

**Experiment tracking** is the process of keeping track of all relevant information from an ML experiment, which includes: source code, environment, data, model, hyperarameters, metrics, etc. depending on the experiment we're running: tuning hyperparameters or updating the data used, for example.  An **ML experiment** is the whole process of building an ML model. It is made of many trials. Each of them is an **experiment run**. Note that a **run artifact** is any file that is associated with an ML run and **experiment metadata** are information about an ML experiment like the source code used, the name of the user, etc.

Experiment tracking are important for **reproducibility** so others can reproduce our work, **organization** to simplify and ease whatever we are working on and **optimization** to make sure we pick the optimal model in function of our needs that might even change.

Generally, we used spreadsheets to store the same information keeping tracks of models and data. However, it is error prone (as we're copying manually), there is no standard format (the way you record might be different from the one someone else would do) and it lacks visibility (need to ask for the spreadsheet) & collaboration (need to understand how information were recorded).
**MLflow** is an open source platform for the machine learning lifecycle (building and maintenaing ML models). In practice, it’s just a Python package that can be installed with `pip`, and it contains
four main modules: *Tracking* (focused on experiment tracking), *Models* (special type of models), *Model Registry* (to manage models) and *Projects*. You can even run your own server in MLflow if you want to collaborate with other people.

The MLflow Tracking module allows you to organize your experiments into runs, and to keep track of: Parameters (can include preprocissing steps and the data path), Metrics (any evaluation metric calculated on training, validation and test sets), Metadata (including tags that can allow to search and filter runs easily), Artifacts (any file generated as a visualization), Models. Along with this information, MLflow automatically logs extra information about the run: Source code (name of the file used tu run the experiment), Version of the code (git commit), Start and end time, Author.
The command `mlflow ui` helps launch the user interface of mlflow. Note that to use the model registry, you need to run the mlflow with some back-end: postgresql, mysql, sqlite or mssql.


## 🛠️ 2.2 Getting started with MLflow
For the purpose of the course, we created a conda environment: 
```sh
conda create -n mlops-zoomcamp python=3.9.7
```
We will activate it: 
```sh
conda activate mlops-zoomcamp
```
and install the necessary [requirements](./notebooks/course/requirements.txt) including `mlflow`:
```sh
pip install -r requirements.txt
```
You can check that everything went well using:
```sh
pip list
```
It will provides installed packages with their versions.
We can then run `mlfow` using:
```sh
mlflow ui --backend-store-uri sqlite:///mlflow.db
```
> This command indicates to mlflow that all metadata should be installed in `sqlite`. We can then use the model registry.

We can now copy the listening address in a navigator to start `mlflow`, and run a [notebook](./notebooks/course/duration-prediction.ipynb) to test this framework using jupyter.


## 📉 2.3 Experiment tracking with MLflow
From basic logins added into the [notebook](./notebooks/course/duration-prediction.ipynb), we will now add hyperparameters tuning and explore their results using the mlflow UI
to determine the best model. Note that selecting the best model depends on our needs but we can also simply use the model tags for filtering and sort the runs by the metric. We will also use [**Autolog**](https://mlflow.org/docs/latest/tracking/autolog), an interesting feature of mlflow enabling login a lot of information with less code. Note that when saving the model, mlflow also keeps track of the environment.


## 🖥️ 2.4 Model Management
Machine Learning lifecycle refers to all the steps needed to build and maintain a machine learning model.
![ML Lifecycle](../images/ML_lifecycle.png)
Model management covers experiment tracking, model versioning and model deployment. The model might needs to be updated in order to scale. Once done, and after deployment, it can then be used for making predictions.

Saving models in folders is error prone as you can overwritte accidently an old model. There is no clear versioning of the models and no model lineage (what data and hyperparameters were used for training and evaluation). `mlflow` proposes better options for saving models. We can save them as artifacts. This will just save the model file to `mlflow`. We can also save them directly as models. This will help saving more information: many flavors depending on the model i.e: python function and xgboost, the environment information either conda indicating the python environment or only requirements with the packages used. Note that it is important to save the preprocessor as for making predictions in the future we will need to preprocess the data. It can be saved as an artifact.

Note that mlflow automatically generates code snippets to indicate how to make predictions using the model saved with the function `log_model`. **Uri**(unique resource identifier) serves to identify a model. The model can even be reetrained and deployed to cloud environments.


## 🧰 2.5 Model Registry
When collaborating a data scientist can send models to deployment for ML engineers. They need to know the change between the current model and the previous one, if they should update hyperparameters, if there is any preprocessing needed and in which environment (dependencies versions) this model should run. Getting answers via a discussion might take time and wouldn't be optimal. There might even be a need to retrain the model. If the engineer is lucky, the data scientist has saved useful information to mlflow. However, the [**model registry**](https://www.mlflow.org/docs/latest/model-registry) can make things even easier. In previous experiments, we used a tracking server running locally to log experiments data (parameters, metrics, artifacts, models). After some time, we may decide some models are ready for production. They can be registered to the model registry so ML engineers an check the production ready models for deploying. Data scientists decide what models are ready for production, and ML engineers move them to different stages (labels): staging -> production or archive after inspecting them. The model registry needs to be complemented with some CI/CD code for deployment.

The training duration, the metric error and the model size are important information for evaluating models to production. Based on that, we will promote the `xg-boost` model to the model registry and put the `GradientBoosting` one to the staging. We will include tags for each model. 

> For testing and comparing models, we downloaded the March data into the [data folder](./notebooks/course/data/):
```sh
# Download the data once in the right folder
curl -O "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2021-03.parquet"
```
After testing we can evaluate models and update the one in production accordingly using our [notebook](./notebooks/course/model-registry.ipynb).

> **Starting MLflow 2.9, model registry stages are deprecated.**
Please use model version tags and aliases instead of stages. For example, instead of `transition_model_version_stage(name, version, stage)` use `set_registered_model_alias(name, alias, version)`. More details [here](https://github.com/mlflow/mlflow/issues/10336) and [here](https://mlflow.org/docs/latest/model-registry.html).



## ☁️ 2.6 MLflow in Practice
We will [simulate different scenarios](./notebooks/course/running-mlflow-scenarios/): a single data scientist participating in an ML competition, a cross-functional team with one data scientist working on an ML model and multiple data scientists working on multiple ML models.

A single data scientist working in an ML competition doesn't need storing information on a remote server, or a model registry. He can still access the interface with the command `mlflow ui`. 

The [second scenario](./notebooks/course/running-mlflow-scenarios/scenario-2.ipynb) requiers sharing information but no need to keep tracks remotely. Launching tracking server:
```sh
mlflow server --backend-store-uri sqlite:///backend.db
```
to interact with other team members might be useful but doesn't need to be on the cloud. Note this is a server, not the UI. A sqlite database would enable using the model registry and artifacts can be stored locally or even on the cloud. Running the tracking server locally, helps to see results from a run in real time before it finishes. Note that here, the metadata are not saved in the artifact root but in the sqlite database.

In the last case with multiple data scientists, sharing information is very important. It allows data scientists to continue experiments and manage together the lyfecicle of the model. Here, AWS is used to host a remote server. Follow the steps described in the file [`mlflow_on_aws.md`](./notebooks/course/mlflow-on-aws.md) to create a new AWS account, connect to the AWS console manageent and launch the tracking server.  Note that the bucket used will be called: `mlflow-runs-artifacts-remote` and the first database will be: `mlflow_db` to keep tracks of experiments. The username will be `mlflow` and the password: `****`. The database endpoint is `mlflow-database.c0fckkq4q0tk.us-east-1.rds.amazonaws.com`.

We will run the server with the command:

`mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:****@mlflow-database.c0fckkq4q0tk.us-east-1.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-runs-artifacts-remote`

If any error with `urlib` packages:

`pip3 install "urllib3<1.27"`. 

Once, running we will check the EC2 instance and copy the public DNS: `ec2-34-227-105-189.compute-1.amazonaws.com`. `mlflow` will be running at: `ec2-34-227-105-189.compute-1.amazonaws.com:5000`.

Even though the instance is running in the cloud, we still need to configure our aws account locally. First, install awscli:

```sh
pip install awscli
```

Now, configure a profile with:

```sh
aws configure --profile magic-maxim
```
Make sure to fill necessary information.

After running the [notebook scenario](./notebooks/course/running-mlflow-scenarios/scenario-3.ipynb), we can then check that everything was stored in the s3 bucket and that the mlflow interface is working properly.

> We will delete the ml_runs or artficats root folder and potential databases after completing each scenario.

To configure mlflow, we need to think of:
- the backend store: where mlflow saves all metadata (metrics, parameters, tags). It can be a local filesystem or a SQLAlchemy compatible database (e.g. SQLite)

- artifacts store: all artifacts stored locallly or remotely (e.g. s3 bucket)

- tracking server: no tracking server, or a localhost or a remote host.




## 🧭 2.7 MLflow: benefits, limitations and alternatives

The tracking server can be easily deployed to the cloud helping to share experiments with other data scientists, collaborate with others to build and deploy models using the model registry and give more visibility of the data science efforts.

Some issues with running a remote (shared) MLflow server are
- Security: you need to restrict access to the server (e.g. access through VPN).
- Scalability: Check [Deploy MLflow on AWS Fargate](https://github.com/aws-samples/amazon-sagemaker-mlflow-fargate) or Check [MLflow at Company Scale](https://www.youtube.com/c/Databricks) by Jean-Denis Lesage for tracking experiments.
- Isolation: you can define standard for naming experiments, models and a set of default tags and also to restrict access to artifacts (e.g. use s3 buckets living in different AWS accounts).

MLflow limitations (and when not to use it):

- Authentication & Users: The open source version of MLflow doesn’t provide any sort of authentication.
- Data versioning: to ensure full reproducibility we need to version the data used to train the model. MLflow doesn’t provide a built-in solution for that but there are a few ways to deal with this limitation.
- Model/Data Monitoring & Alerting: this is outside of the scope of MLflow and currently there are more suitable tools for doing this.

Some paid MLflow alternatives include: [Neptune](https://neptune.ai/), [Comet](https://www.comet.com/site/), [Weights & Biases](https://wandb.ai/site) and [many more](https://neptune.ai/blog/best-ml-experiment-tracking-tools).



## 📝 2.8 Homework
Homework for this module is available [here.](notebooks/homework/homework_02.ipynb).

---
