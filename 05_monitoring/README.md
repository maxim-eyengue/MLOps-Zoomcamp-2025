![MLOps Zoomcamp](../images/banner-2025.jpg)

# 🚀 MLOps Zoomcamp – Week 5: Model Monitoring
**Instructors:** Emeli Dral, Alexey Grigorev

---

## 📌 5.1 Introduction to ML monitoring    
Monitoring machine learning models in production is crucial because model quality typically degrades over time, requiring ongoing performance assessment and issue detection. Traditional service health metrics (e.g., uptime, memory usage, latency) must be complemented with ML-specific metrics related to data and model behavior to ensure comprehensive monitoring. Key monitoring areas include service health, model performance, data quality and integrity, and detection of data and concept drift.

#### Core Groups of Monitoring Metrics
A good starting point for model monitoring is the combination of the following metrics:
- **Service Health Metrics:** Ensure the underlying service is operational: **does it work?** This is a fundamental prerequisite for any ML service.
- **Model Performance Metrics:** Need to check **how good are the models?** and **if anything breaks**. This depends on the problem statement:
  - Ranking problems use ranking metrics.
  - Regression problems use metrics like Mean Absolute Error (MAE) or Mean Absolute Percentage Error (MAPE).
  - Classification problems use metrics such as log loss, precision, and recall.
- **Data Quality and Integrity Metrics:** Include missing value counts, value range checks, and type consistency to catch input data issues early. Here we check **where the ML process breaks**, or **where to dig further.**
- **Data Drift and Concept Drift:** are **metrics** used to compare distributions of current input data, model outputs, and target variables against reference datasets to detect shifts that could signal performance degradation. This answer to: **is the model still relevant?**

#### Additional Monitoring Considerations
- **Performance by segment:** Metrics can be segmented by categories or groups to detect quality variation across subpopulations. 
- **Model bias or fairness:** Monitoring for model bias and fairness is critical in sensitive areas such as healthcare or finance to ensure equitable performance.
- **Outliers:** Outlier detection can be used when individual errors are costly, enabling manual review to reduce risks.
- **Explainability:** For recommender systems, tracking user trust and explanation consistency is important especially when models are frequently retrained and updated automatically.

#### Architecture and Implementation of Monitoring
Existing production monitoring infrastructure (e.g., Prometheus and Grafana) can be leveraged to include ML model metrics, facilitating integration and visualization. When there aren't any production monitoring it is still possible to use some BI Tools like Tableau, Looker or Power BI to analyze predictions by creating dashboards.

Batch models are typically easier to monitor using batch metrics such as drift detection and performance metrics calculated on grouped data sets (a reference data and a most recent one). Online (non-batch) models may require a hybrid approach: real-time calculation of simple metrics (e.g., missing values, range variations) and batch aggregation/windowing for complex metrics like data drift and model performance (because those ones should be calculated on the top of the dataset and not on a single object).

#### Proposed Monitoring Pipeline Architecture
| Step                      | Description                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| 1. Prediction Logging     | Collect prediction logs from batch or online services as the primary data source             |
| 2. Batch Processing       | Use batch pipelines to read logs, calculate ML and data-related metrics, and store results   |
| 3. Metrics Storage        | Store calculated metrics in a database (e.g., PostgreSQL)                                   |
| 4. Visualization & Alerts | Use dashboard tools (e.g., Grafana) to visualize metrics and set alerts                      |

This monitoring scheme supports both batch and online models as it builds monitoring on top of prediction logs.

#### Tools and Technologies for Monitoring
- **Prefect**: Orchestrates batch jobs for metric calculation and data processing.
- **Evidently AI Library**: Provides ready-to-use functions for metric calculation and distribution comparison, simplifying implementation.
- **PostgreSQL**: Stores aggregated metrics for querying and visualization.
- **Grafana**: Visualizes metrics with customizable dashboards and alerting capabilities.

> **💡 Key Insight:** Monitoring ML models requires combining traditional service health checks with specialized metrics addressing data quality, model performance, and data distribution shifts to detect and mitigate degradation effectively.  

> The integration of batch and online monitoring techniques enables comprehensive coverage regardless of deployment style.  

> Leveraging existing production monitoring tools and open-source libraries simplifies the implementation and maintenance of ML monitoring systems.  
                      
## 🛠️ 5.2 Environment setup    
Note we are currently working on a [prepared conda environment](../01_intro/README.md#️-12-environment-preparation). We need to make sure to install all the [required](./notebooks/course/requirements.txt) libaries (prefect for pipelines orchestration, tqdm for progressive bars, requests to load data from Internet, joblib to save and load a Python object,some libraries to work with postgres databases and other to work with data in Python):
```sh
pip install -r requirements.txt
```
> Ps: Make sure to be in the correct directory.

We will also use **Docker Compose.** It is a tool used to build and run multi-container Docker applications through a YAML configuration file where all services are listed and configured. For example, we can use the [Docker Compose file](./notebooks/course/docker-compose.yml) syntax to define services, volumes, and networks. Note that Docker Compose is automatically [installed with **Docker Desktop**](../01_intro/README.md#️-12-environment-preparation).

#### Volumes and Networks Configuration
- **Volumes** are used to persist data generated by and used by Docker containers. For example, a volume can be created for Grafana to store dashboards and data source configurations, ensuring data persists across container restarts.
- **Networks** allow services to communicate selectively. In our case, we will need two custom networks: `frontier` and `backtier`. This setup enables controlled communication between services, e.g., database and Grafana communicate over both networks, while some services are restricted to one network for security and organization.

#### Services Definition

Here is a table higlighting the services tthat we defined:

| Service  | Image      | Purpose                         | Networks          | Key Configurations                        |
|----------|------------|--------------------------------|-------------------|------------------------------------------|
| Postgres | `postgres` | Database service                | `backtier`        | Always restart, environment vars for password, no browser access ports exposed |
| Adminer  | `adminer`  | Database management tool       | `backtier`, `frontier` | Always restart, port 8080 exposed for browser access |
| Grafana  | `grafana`  | Dashboarding and visualization | `backtier`, `frontier` | Always restart, volumes for dashboards and data source configs, user specified |

- The **Postgres** container runs the database with a password environment variable and is restricted to the `backtier` network for security.
- **Adminer** serves as a native Postgres database management tool, connected to both networks to allow database access and browser interface access.
- **Grafana** is configured with volumes for persistent data and the data source configuration, connected to both networks to allow browser access and database communication.

#### Grafana Data Source Configuration

We create a configuration folder [`config`](./notebooks/course/config/) to hold Grafana data source settings, specifically a YAML file defining the PostgreSQL data source.
The data source YAML specifies:
- Config version.
- Data source name and type (`postgres`).
- Access mode through proxy.
- Database connection parameters matching the Docker Compose environment variables such as database name, user, password, and SSL mode disabled for simplicity.

#### Running and Accessing Services
We start the entire multi-container application with the command `docker compose up --build`, which builds and runs all services as defined in the Compose file. After successful container creation, services can be accessed via browser:
- **Grafana** runs on [port 3000](http://127.0.0.1:3000) with default login credentials `admin/admin`, prompting password reset on first login. It provides an interface for dashboards, panels, and data source management.
- **Adminer** runs on [port 8080](http://127.0.0.1:8080), providing a web interface to manage the Postgres database content conveniently.

> **💡 Key Insight:** Using Docker Compose with volumes and custom networks allows for modular, persistent, and secure multi-service applications, enabling easy management and interaction through web interfaces like Grafana and Adminer.  
           
To stop running the containers, we can use Ctrl+C and then `docker-compose down`.


## 📉 5.3 Prepare reference and model
To calculate data drift, we need to get a **reference dataset.** Our focus is now on creating all the artifacts (data and models) we need for building a **grafana dashboard**. For this purpose, we will use a [notebook](./notebooks/course/baseline_model_nyc_taxi_data.ipynb).

> **💡 Key Insight:** Using the validation data as reference data allows comparison between current production data and the "known good" data, facilitating detection of data drift and ensuring model reliability over time.
 

## 🖥️ 5.4 Evidently metrics calculation   
With help of Evidently reports, we can compute many different metrics related to ML pipelines. We will quickly build Evidently report toget metrics that can be used for our dashboard for monitoring. For that we will use the previous [notebook](./notebooks/course/baseline_model_nyc_taxi_data.ipynb).

A **report object** in Evidently groups multiple metrics to calculate. You specify which metrics to include when creating this report, allowing flexible metric selection. Commonly included metrics are **prediction drift**, **dataset drift**, and **missing values**. Prediction drift is important for analyzing data quality and stability, typically calculated on the prediction column. Dataset drift checks for distribution changes across features between reference and current datasets, and missing values metrics reveal data completeness issues.

The HTML report shows the metrics specified, such as prediction drift and dataset drift. If drift is not detected, it suggests the training and validation splits were successful and stable. Missing values are also reported, highlighting potential data quality issues but not necessarily indicating drift.

For automated pipelines or monitoring, working with the report in **dictionary format** is preferable over HTML. This allows programmatic access to specific metric values for decision-making. Using `report.dict()` converts the report into a Python dictionary, enabling extraction of individual metrics like prediction drift score, number of drifted columns, and share of missing values.


> **💡 Key Insight:** Storing metrics as a list rather than a dictionary with named keys allows Evidently to flexibly handle multiple metrics of the same type with different parameters, which is crucial for complex monitoring scenarios.
  

> **ℹ️ Note:** The HTML report format is excellent for exploratory analysis and quick visualization, while the dictionary format is essential for automation and integration into monitoring pipelines.
  


## 🧰 5.5 Evidently Monitoring Dashboard   
Evidently monitoring dashboards enable quick setup of data and model monitoring, particularly useful for batch models without existing monitoring infrastructure. The core approach is to calculate reports regularly and store them for visualization and analysis. We will use a [notebook](./notebooks/course/baseline_model_nyc_taxi_data.ipynb) for doing that.

#### Creating and Adding Reports
Reports summarize dataset quality and model metrics, including configuration details (e.g., target column, prediction column), summary statistics per column, missing values, and correlations. These reports form the basis for monitoring. They should be generated regularly with a specific datetime to associate dashboard plots with particular dates, enabling time series analysis. After generating a report, we can add it to the project workspace for persistent storage and later visualization.

#### Running Evidently UI and Viewing Reports
Evidently UI can be launched from the terminal with default options to serve the monitoring dashboard locally:
```sh
evidently ui
```
It displays a list of projects and their reports, allowing users to browse and view detailed reports similar to those seen in notebooks. Reports can be tagged with text or metadata to facilitate searching and identification within the dashboard interface.

#### Configuring Dashboards and Panels
Dashboards can be added and managed within projects, and panels are their building blocks. They display counters, plots, or other metrics derived from the reports. Types of panels include:
- **Dashboard Panel Counter:** Displays simple counts or aggregated metrics without filters or aggregation.
- **Dashboard Panel Plot:** Visualizes metrics over time or categories using plot types like line, bar, or scatter.

> Note that it is important to save the dashboard configuration after adding or modifying panels to preserve changes.

#### Enhancing Dashboard Usefulness with Multiple Data Points
- Adding multiple reports with different datetime values enables trend analysis and a more informative dashboard by showing changes over time.
- Regularly scheduled generation and addition of evidently reports (e.g., daily, weekly) automate the monitoring process and support ongoing data and model quality checks.

> **💡 Key Insight:** Evidently dashboards provide an accessible, fast way to start monitoring batch models and data quality without existing infrastructure, by leveraging regularly generated reports and flexible dashboard panels for visualization and tracking over time.
  

## 🧭 5.6 Dummy monitoring
We will create a [script](./notebooks/course/dummy_metrics_calculation.py) to calculate some dummy metrics and load them into our database. We want to create a database, create a test table and add metrics row by row to that table. After writing the script, we can activate services with Docker Compose:
```sh
docker-compose up --build -d
```
`-d` helps to run in detached mode so to get the access back to the terminal after the execution of the command.   
We can now execute the script: `python dummy_metrics_calculation.py`.
Connecting to [Adminer](http://127.0.0.1:8080) helps to manage our Postgres database and verify that the data is sent. We can also log into [Grafana](http://127.0.0.1:3000) to create dashboards and visualize the data.

> **ℹ️ Note:** The approach of generating dummy monitoring data with controlled timing and visualization helps simulate production-like batch data flows, enabling testing of monitoring pipelines without relying on real system metrics.  
    
## 🖥️ 5.7 Data quality monitoring

## 📉 5.8 Save Grafana Dashboard

## 🧰 5.9 Debugging with test suites and reports

## 📝 5.10 Homework
Homework for this module is available [here.](notebooks/homework/homework_05.ipynb).

---
