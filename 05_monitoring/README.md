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
