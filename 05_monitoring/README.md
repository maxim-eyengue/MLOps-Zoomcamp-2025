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
           



## 📉 5.3 Prepare reference and model

## 🖥️ 5.4 Evidently metrics calculation   

## 🧰 5.5 Evidently Monitoring Dashboard   

## 🧭 5.6 Dummy monitoring

## 🖥️ 5.7 Data quality monitoring

## 📉 5.8 Save Grafana Dashboard

## 🧰 5.9 Debugging with test suites and reports

## 📝 5.10 Homework
Homework for this module is available [here.](notebooks/homework/homework_05.ipynb).

---
