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

### 3.3.4 Deploying Your Workflow
The workflow evolves from a notebook to a script enhanced with Prefect tasks and flow decorators, improving resilience and observability. The next step is deploying this workflow on a local Prefect server to enable scheduling and collaboration features.

To initialize a Prefect Project, run `prefect project init` in the project directory. This will create essential files:
  - `.prefectignore`: prevents automatic code pushes from Prefect to Git repositories.
  - `deployment.yaml`: useful for templating multiple deployments.
  - `prefect.yaml`: the main configuration file for the project and deployment build, pull, and push steps.
  - `.prefect` folder: contains shorthand convenience files.
Note that these files are not overwritten if they already exist: manual deletion is required to reinitialize properly.

#### Prefect.yaml Configuration

- The `prefect.yaml` file includes metadata such as project name, Prefect version (e.g., 2.10.8), and repository details.
- Build and push steps (e.g., Docker image creation or pushing to AWS S3) can be configured but are optional; in this context, only the pull step is active, which clones the repository code during deployment runs   .

#### Work Pools and Workers

- A **work pool** is created to manage where and how flow runs execute. Types include:
  - Process (local subprocesses)
  - Kubernetes
  - Serverless options like Cloud Run, Azure Container Instances, or Amazon ECS
- In this tutorial, a process work pool named "Zoom pool" is created for local execution.
- Workers pull tasks from the work pool and execute flows, enabling distributed or parallel processing    .

#### Deploying the Flow

- Deployment is performed using the CLI command:

  ```bash
  prefect deploy 3.4/orchestrate.py:main_flow --name Taxi1 --work-pool zoompool
  ```

  - `3.4/orchestrate.py:main_flow` specifies the flow entry point.
  - `--name` assigns a deployment name.
  - `--work-pool` specifies the pool from which workers will pull tasks.
- Successful deployments are confirmed with messages like "main flow Taxi1 successfully created"   .

#### Starting Workers and Running Flows

- Workers are started with:

  ```bash
  prefect worker start -p zoompool
  ```

  - Optional `-T process` can specify worker type.
  - Workers continuously poll the specified work pool for available flow runs.
- Flow runs can be triggered either through the Prefect UI or CLI.
- Upon triggering, the deployment creates a flow run, which the worker picks up and executes according to the configured infrastructure and flow logic    .

#### Observing Flow Execution and Results

- The Prefect UI provides real-time monitoring of flow runs, including scheduling status, logs, and results such as validation RMSE.
- The terminal output confirms worker activity and successful completion of flow runs.
- The project repository includes necessary data files (e.g., parquet files) to ensure data availability during execution.
- Future improvements include leveraging cloud storage like S3 for data to facilitate collaboration and scalability    .

#### Benefits of Deployment

- Deployments enable:
  - Scheduling of workflows.
  - Collaboration among team members via shared infrastructure.
  - More robust and scalable production workflows beyond local script execution   .

---

> **💡 Key Insight:** Deploying workflows with Prefect projects and work pools abstracts execution infrastructure, supports scheduling, and enhances collaboration, marking a critical step towards production-grade MLOps.  
   
### 3.3.5 Working with Deployments
#### Prefect Blocks for AWS S3 Integration
- Prefect blocks enable modular, reusable components for workflows; AWS-related blocks such as S3 bucket and AWS credentials blocks facilitate integration with AWS services.   
- Installation of `prefect-aws` package is required to use AWS blocks; documentation and examples are available on Prefect's official GitHub and docs site for reference.   
- AWS credentials block requires AWS Access Key ID and Secret Access Key; sensitive information should be protected (e.g., environment variables) and not publicly exposed.   
- AWS IAM setup involves creating a user with appropriate S3 access permissions (e.g., full S3 access or restricted policies) to enable read/write operations on S3 buckets.   
- Blocks are Python classes with validation (using Pydantic), registered and saved to the Prefect server to be accessible during workflow runs; overwriting existing blocks is supported.   
- Loading and using saved blocks from the Prefect server allows decoupling credentials and bucket configuration from code, enhancing security and reusability.   
- Prefect CLI commands like `prefect block ls` and `prefect block register` help manage block types and ensure server awareness of available blocks.   
- Blocks can be created or edited via Prefect UI or Python code, providing flexibility in managing infrastructure components.   

#### Loading Data from S3 in Prefect Flows
- Modify Prefect flow to load data directly from S3 by loading the S3 bucket block and using methods like `download_folder_to_path` to retrieve entire folders to local paths.   
- This approach avoids storing data in GitHub repositories and enables dynamic data retrieval during flow execution, supporting better data management and security practices.   
- Running the flow locally with S3 integration verifies data download and processing, with all execution details captured in the Prefect UI for monitoring.   

#### Creating and Managing Multiple Deployments
- Prefect projects support multiple deployments from a single codebase; deployments are defined in a `deployment.yaml` file specifying entry points, flow names, work pools, schedules, and parameters.   
- Example: one deployment uses local data, another uses S3 data, differentiated by entry point scripts and flow names; both can be deployed simultaneously with `prefect deploy --all`.   
- Multiple deployments enhance flexibility by allowing different data sources or configurations without duplicating codebases.   

#### Adding Artifacts for Enhanced Reporting
- Prefect supports creating artifacts such as markdown reports that appear in the UI, useful for sharing metrics like RMSE after model training.   
- Markdown artifacts can include formatted tables with dynamic content (e.g., dates, metrics) using Python f-strings and `create_markdown_artifact` from Prefect.   
- Artifacts provide historical records of model performance, aiding comparison between runs and improving transparency of workflow outcomes.   

#### Running Deployments and Monitoring
- Deployments can be run from the command line using `prefect deployment run` with deployment identifiers; workers must be running to execute flows.   
- Flow runs execute in isolated temporary directories, with progress and logs visible in the Prefect UI, including status updates like downloading data and validation results.   
- Artifacts generated during runs are accessible in the UI, providing instant feedback on model metrics or other outputs.  

#### Parameterization and Scheduling of Flows
- Flow runs support parameter overrides via the UI, allowing users to customize inputs such as dates or filenames per run without changing code.  
- Deployments can have schedules added through the UI or CLI to automate flow execution at intervals (e.g., every 10 minutes or 60 seconds), supporting recurring workflows.   
- Schedules can be defined with interval, cron, or repeating rules; some complex schedules may require CLI or YAML configuration as UI support is limited.   
- CLI commands like `prefect deployment set schedule` enable setting or updating schedules programmatically.  

> **💡 Key Insight (from source):** Prefect blocks combined with deployments, artifacts, and scheduling provide a powerful, modular framework for productionizing workflows with dynamic data sources like S3, enabling automation, monitoring, and reproducibility. 

### 3.3.6 Prefect Cloud
#### Prefect Cloud Overview and Architecture
- **Prefect Cloud** is a hosted orchestration platform run by the Prefect company, allowing users to avoid managing their own servers while gaining enhanced pipeline orchestration and monitoring features   .
- It uses a **hybrid model**: user code and workers run on local or user-chosen infrastructure, while Prefect Cloud manages metadata (flow states, scheduling info) without storing full flow code or data   .
- Workers connect to Prefect Cloud’s API to receive scheduled flow runs from work pools and send back metadata updates, which are displayed in the Prefect Cloud UI  .

#### Profiles and Server Connection
- Prefect profiles manage connection configurations to different Prefect servers (local or cloud); users can list and switch profiles to change the server their client communicates with  .
- Logging into Prefect Cloud is done via the CLI using `prefect cloud login`, which supports OAuth-based web login or API key authentication; API keys can be generated and managed from the Prefect Cloud UI    .
- Profile information, including API keys and server URLs, is stored locally in the `.prefect/profiles.toml` file, enabling multiple profile setups for different environments   .

#### Setting Up Workers and Work Pools
- Workers are started locally with commands like `prefect worker start -p  -t ` to connect them to a specific work pool on Prefect Cloud; work pools can be typed by infrastructure (e.g., process, Kubernetes, Docker) and support concurrency limits    .
- Creating a worker without an existing work pool will automatically create a work pool of the specified type, facilitating management of distributed execution resources   .

#### Deployment and Flow Management
- Deployments are created using `prefect deploy --all`, which reads deployment configuration files (`prefect.yaml`, `deployment.yaml`) and registers flows on Prefect Cloud   .
- The Prefect Cloud UI allows users to view deployments, check their state (pending, running, completed), and monitor flow runs with detailed visibility into task runs, subflows, artifacts, and results   .

#### Collaboration and Workspaces
- Prefect Cloud supports **workspaces**, enabling team collaboration by inviting others to shared environments, a feature not available in local Prefect server setups   .
- Security practices include SOC 2 Type 2 compliance and role-based authentication options (e.g., SSO integration via Okta) for enterprise use cases  .

#### Cloud-Only Features: Event Feed and Automations
- Prefect Cloud provides an **event feed** showing detailed, filterable logs of flow and task events, which is not available in the open-source server version   .
- **Automations** enable users to trigger actions based on flow run state changes (e.g., scheduled, completed, failed). Triggers can initiate notifications or other deployments, enhancing operational workflows   .
- Notification blocks support various channels such as email, Slack, and PagerDuty; users can create and customize these blocks to send alerts when flows enter specified states    .

#### Key Commands and File Structures
| Command/Concept                  | Purpose/Description                                                                                         |
|--------------------------------|------------------------------------------------------------------------------------------------------------|
| `prefect profile ls`            | Lists all available Prefect profiles and their associated servers                                          |
| `prefect cloud login`           | Authenticates CLI with Prefect Cloud via web login or API key                                              |
| `prefect worker start -p  -t ` | Starts a local worker connected to a specified work pool and infrastructure type                      |
| `prefect deploy --all`          | Deploys all flows defined in configuration files to Prefect Cloud                                          |
| `.prefect/profiles.toml`        | Local storage of Prefect profiles, including API keys and server URLs                                      |
| `prefect.yaml` & `deployment.yaml` | Configuration files defining flow deployments and settings                                               |

#### Important Notes
> **❗ Important:** Prefect Cloud does not receive or store the actual flow code or data—only metadata about flow states and execution, preserving user data locality and security.  
   

> **ℹ️ Note:** Switching between local and cloud servers requires changing profiles and ensuring workers and deployments are connected to the correct server.  
   

> **💡 Key Insight:** Automations and event feeds in Prefect Cloud enable proactive monitoring and response to pipeline events, improving workflow reliability and team collaboration.  
  

## 📝 3.4 Homework
Homework for this module is available [here.](notebooks/homework/homework_03.ipynb).

---
