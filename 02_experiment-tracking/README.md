![MLOps Zoomcamp](../images/banner-2025.jpg)

# 🚀 MLOps Zoomcamp – Week 2: Introduction

**Instructor:** Cristian Martinez, Alexey Grigorev

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


### 🖥️ 2.4 Model Management
Machine Learning lifecycle refers to all the steps needed to build and maintain a machine learning model.
![ML Lifecycle](../images/ML_lifecycle.png)
Model management covers experiment tracking, model versioning and model deployment. The model might nees to be updated in order to scale. Once done, and after deployment, it can then be used for making predictions.
Saving models in folders is error prone as you can overwritte accidently an old model. There is no clear versioning of the models and no model lineage (what data and hyperparameters were used for training and evaluation). `mlflow` proposes better options for saving models. We can save it as an artifact. This will just save the model file to mlflow. We can also save it directly as a model. This will help saving more information: many flavors depending on the model i.e: python function and xgboost, the environment information either conda indicating the python environment or only requirements with the packages used. Note that it is important to save the preprocessor as for making predictions in the future we will need to preprocess the data. It can be saved as an artifact.

Note that mlflow automatically generates code snippets to indicate how to make predictions using the model saved with the function `log_model`. **Uri**(unique resource identifier) serves to identify a model.

### ☁️ 

### 🧰 




## 🧭 




## 📝 2.8 Homework
Homework for this module is available [here.](notebooks/homework/homework_02.ipynb).

---