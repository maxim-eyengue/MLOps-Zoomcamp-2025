![MLOps Zoomcamp](../images/banner-2025.jpg)

# 🚀 MLOps Zoomcamp – Week 3: Orchestration & ML Pipelines

**Instructors:** Alexey Grigorev, Jeff Hale, Bianca Hoch

---

## 📌 3.1 Introduction to ML Pipelines 
A **training pipeline** is a sequence of steps executed in order to train a machine learning model, aiming for reproducibility, parameterization, and easy reruns. Pipelines improve upon raw Jupyter notebooks by making workflows maintainable, reliable, and easier to re-execute compared to messy, long notebooks that are difficult to understand or rerun. **Workflow orchestration** is a broader term from data engineering describing how steps are scheduled and organized. ML learning pipelines are a specific application (or workflows) focused on producing ML models.

A Machine Learning Pipeline is nothing more than a sequence of steps needed to produce an ML model:  
  1. **Data ingestion:** Downloading or acquiring data from sources, sometimes called ingestion in data engineering.  
  2. **Data transformation:** Processing data, such as converting columns to datetime, computing new features like duration, filtering outliers, and aggregation.  
  3. **Feature engineering and data preparation:** Creating feature matrices (X) and target arrays (Y) for model input. Note that feature engineering may occur between transformation and preparation.  
  4. **Hyperparameter tuning:** Searching for the best model parameters, using libraries like Hyperopt, to optimize model performance.  
  5. **Model training:** Using the best parameters to train the final model.  
  6. **Model registration:** Saving the trained model to a model registry for deployment or further use.

Converting a notebook into a Python script with well-structured functions for each step improves maintainability and modularity, allowing unit tests and easier updates. Such a script can be executed sequentially, making it a simple but effective pipeline implementation. However using scripts for running pipelines ahs some challenges:
- Running scripts manually or via cron jobs on local machines is impractical for collaboration, scheduling, and scalability.  
- Challenges include coordinating multiple jobs, centralized management, ensuring the latest code version runs, and scaling beyond a single computer.  
- Handling failures (e.g., temporary network issues during data download) requires retry mechanisms, which complicate code and reduce reliability.

Fortunately, **Workflow Orchestration Tools** are very useful: 
- They centralize code management on servers, enable team collaboration, support scheduling, and scale resources as needed.  
- They provide monitoring, alerting, and notifications to manage pipeline health and failures effectively.  
- With **dependency management**, they ensure steps run in the correct order and subsequent steps wait for prior steps to complete successfully.

### Examples of Workflow Orchestration Tools  
| Tool          | Description                                       | Focus Area                      |
|---------------|---------------------------------------------------|--------------------------------|
| Airflow       | Most popular, general-purpose, complex to use     | Data engineering & ML           |
| Prefect       | General-purpose workflow orchestration            | Data engineering & ML           |
| Mage          | General-purpose workflow orchestration            | Data engineering & ML           |
| Luigi         | General-purpose workflow orchestration            | Data engineering & ML           |
| Kubeflow Pipelines | ML-specific pipeline orchestration           | Machine learning                |
| MLflow Pipelines   | ML-specific pipeline orchestration           | Machine learning                |

General-purpose tools work well for diverse tasks including ML and data engineering, offering flexibility but sometimes complexity. ML-specific tools focus on machine learning pipelines, often less flexible but more specialized for model training workflows.

> **💡 PS:** Moving from notebooks to structured pipelines and using orchestration tools is essential for scalable, maintainable, and reliable machine learning workflows in production environments.  
                    


## 🛠️ 3.2 Turning the Notebook into a Python Script
Let's run an instance of **MLflow**:
```sh
mlflow server \
    --backend-store-uri sqlite:///mlflow.db
```
We can then open our [notebook](./notebooks/course/duration-prediction.ipynb) to do some experiments with `MLFlow`. To convert our notebook to a python script, we use the command:
```sh
jupyter nbconvert --to=script duration-prediction.ipynb
```
We will update that [script](./notebooks/course/duration-prediction.py).
The code is refactored into functions for modularity:
  - `read_data` constructs URLs dynamically based on year and month parameters.
  - `create_X` handles feature matrix creation, with logic to fit or reuse a dictionary vectorizer.
  - `train_model` encapsulates the model training process, accepting parameters including the dictionary vectorizer to maintain consistency between training and validation data transformations.
  - A `run` or `main` function is created to orchestrate reading data, feature engineering, model training, and evaluation, supporting flexible execution with different parameters  .

## Parameterization and Testing
Hard-coded year and month parameters are replaced with command-line arguments using `argparse`, allowing users to specify these values dynamically when running the script. The script is tested with specific year and month inputs to verify functionality and debug minor issues like variable names:
```sh
python duration-prediction.py --year=2021 --month=1
```

The current pipeline lacks automatic retry and failure handling; these are identified as future improvements best handled by integrating a **workflow orchestration tool** to manage retries and error handling robustly. The foundation is now ready for orchestration tools to be applied, but even without orchestration, the pipeline can be executed manually to produce models consistently.


> **💡 Key Insight:** Converting a notebook into a script with modular functions and parameterization is a crucial step toward reliable, repeatable ML pipelines and prepares the codebase for integration with orchestration tools for automation and robustness.
    


## 📉 3.3 Using an Orchestrator
### 🖥️ 3.3.1 Introduction to Workflow Orchestration
Workflow orchestration manages complex ML pipelines involving data fetching, cleaning, feature engineering, model training, and serving, often using tools like Python scripts, pandas, scikit-learn, XGBoost, MLflow, and frameworks such as Flask or FastAPI for deployment.

Some common Challenges in Building ML Pipelines include:

- ML workflows commonly involve multiple failure points during data manipulation, reading, writing, and integration across systems, making fault tolerance critical since failures are frequent in distributed environments.
- Setting up pipelines requires handling scheduling (e.g., daily runs), logging, retry mechanisms, notifications on success or failure, and managing dependencies among tasks, which can be complex and time-consuming without orchestration tools.
- Visualizing and managing dependencies in pipelines that may branch or have complex flows can be difficult.
- Caching intermediate results to avoid redundant computation is desirable but challenging to implement correctly.
- Collaboration and usability enhancements, such as allowing less technical team members to trigger workflows via user interfaces, add further complexity to pipeline development and maintenance.

This is where Prefect comes in, simplifying Orchestration:

- Prefect is a Python workflow orchestration tool designed to orchestrate and observe workflows at scale with flexibility, supporting asynchronous execution, retries, parallelization (e.g., with Dask), and integration with various cloud providers and data tools.
- Prefect provides a user interface that visualizes complex dependency graphs and shows real-time workflow state, enabling easier monitoring and debugging of ML pipelines.
- The overarching goal of using Prefect in ML workflows is to reduce uncertainty and manual effort in pipeline management, making workflows resilient, observable, and easier to maintain .

> **💡 Key Insight:** Workflow orchestration tools like Prefect help address the inherent complexity and failure proneness of ML pipelines by automating scheduling, retries, logging, dependency management, caching, and collaboration, thus enabling more reliable and scalable ML operations.  
   
### 🧰 3.3.2 Introduction to Prefect
[Prefect](https://docs.prefect.io/v3/get-started) is a flexible framework designed to convert Python code into robust workflows, enhancing resilience to downtime and unexpected failures. It provides an open-source library installable via pip for immediate use:
```sh
pip install -U prefect
```

Prefect Server includes:
  - **Orchestration API:** A REST API handling workflow metadata.
  - **Database:** By default, a local SQLite database stores workflow metadata configured during installation.
  - **Server UI:** Visualizes workflows and their status centrally, aiding monitoring and debugging.

Self-hosting Prefect Server involves running the orchestration API, database, and UI locally.

Key Prefect Terminology and Concepts
| Term       | Description                                                                                      | Example/Notes                                                                                 |
|------------|------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| **Task**   | Equivalent to a Python function: takes inputs, performs work, produces output                    | Decorated with `@task` to identify it as a Prefect task                                      |
| **Flow**   | Container for workflow logic: can call multiple tasks and manage their dependencies             | Decorated with `@flow`; acts as a parent function orchestrating tasks                        |
| **Subflow**| A flow called by another flow, enabling hierarchical workflows                                   | Parent flow calls subflows, which may call their own tasks or flows                         |

> Decorators `@task` and `@flow` are essential for converting Python functions into Prefect workflows; they can accept arguments to add orchestration metadata such as retry policies or descriptive names visible in the UI.

Possible set-up for running Prefect Locally:
  1. Clone a GitHub repository containing a pinned Prefect version in `requirements.txt` and pre-built flows. You can also simply installl prefect with `pip install -U prefect`.
  2. Create and activate a new conda environment with Python 3.9.12, then install [dependencies](./notebooks/course/requirements.txt). This has already been done as part of the zoomcamp.
  3. Start Prefect Server locally by running `prefect server start` in a terminal to launch API, database, and UI.
  4. Configure the Prefect CLI to point to the local API URL to send workflow metadata to the UI usin: `prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`.
  5. Run Prefect flows/scripts against the server and observe real-time logs and flow status updates in the UI. For that you should launch the UI address in your navigator: `http://127.0.0.1:4200`. You can now run a [test script](./notebooks/course/prefect/3.2/cat_facts.py) with one flow using only a task: `python cat_facts.py`. Changes are visible on the UI. We can also run [another script](./notebooks/course/prefect/3.2/cat_dog_facts.py) with a flow running subflows: `python cat_dog_facts.py`.

Note that Prefect Cloud offers managed hosting of the orchestration API, UI, and database for you, removing the need for self-hosting. It also includes additional features and a free tier, making it accessible for users who prefer a cloud solution.

> **💡 Key Insight:** Prefect’s combination of task/flow decorators, retry logic, and a centralized UI provides a powerful toolkit to build, run, and monitor robust Python workflows that can gracefully handle failures and provide detailed runtime insights.


### 🧭 3.3.3 Prefect Workflow
The [explore notebook](./notebooks/course/prefect/3.3/duration_prediction_explore.ipynb) is different from the [module 2 notebook](./notebooks/course/prefect/3.3/duration_prediction_original.ipynb) that we will re-use as it contains information about data types. We will orchestrate the [python script](./notebooks/course/prefect/3.3/orchestrate_pre_prefect.py) from that original notebook to get a [final one](./notebooks/course/prefect/3.3/orchestrate.py) that we can use with Prefect. Note that it is important to add DocStrings to functions as they provide useful information to anyone that would want to use them. We will also create [an orchestration script](./notebooks/course/orchestrate-prefect.py) from this [module script](./notebooks/course/duration-prediction.py). Note that adding caching can  help save some time in your development.
For running [this module orchestration script](./notebooks/course/orchestrate-prefect.py) we will:
- Launch `MLFlow`:
```sh
mlflow server \
    --backend-store-uri sqlite:///mlflow.db
```
- Launch `Prefect`:
```sh
prefect server start
```
- Configure Prefect locally:
```sh
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```
- Run the orchestration script:
```sh
python orchestrate-prefect.py --year=2021 --month=1
```


## 📝 3.4 Homework
Homework for this module is available [here.](notebooks/homework/homework_03.ipynb).

---