# 1. Introduction

Instructor: Alexey Grigorev

## 1.1 Introduction
MLOPS also know as Machine Learning Operations is a set of bets practices for putting Machine Learning models into production. The course will tackle best practices and tools for that. As example think of how to predict the duraation of a drive when taking a taxi. In the simplest way we can thnk of threes teps for a ML project:
design: do we need ML for solving this problem or is there something simpler, train: build the best model to reach our goal, operate: apply the model to new data. The model can be deployed via a web-service (API) so a user ask for a service and get a response. Once, the model is deployed, the operate stage helps make sure that the model is performing well and not becoming worse woth time or new data.



## 1.2 Environment preparation

### 1.2.1 GitHub Codespaces
This is for setting our environment. First you have to login a github account. Then, you create a new repository for the machine learning zoomcamp. Make sure to add a README file for the description and to put the repository as public. 
After creating the repo, click on code and then on codespaces to create a codespace on main. The advantage of this codespace is that some tools like Python, docker, docker-compose, node.js are already installed. 
However, working from the browser is not always convenient: running jupyter notebooks or mlflow, we need to be able to forward ports or connect to services through our computer. For that we will open visual studio code desktop from the interface (note that codespaces extension is required). In the terminal we will then download and install anaconda: 
```sh
# Download anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
# Install Anaconda
bash Anaconda3-2022.05-Linux-x86_64.sh
```
After completing the installation, and grantig required access, we can then open jupyter from our terminal
```sh
# Check python version
python -V
# Open jupyter notebook
jupyter
```
You can check the `PORTS` section to visualize the port mapping between our local machine and our GitHub codespace.


### 1.2.2 VM in AWS or Locally with Linux

You can also rent an instance in the cloud but this option is more expensive. Finally it is possible to setup everything locally. Using the recommended development environment Linux, here are some steps to follow:

#### Step 1: Download and install the Anaconda distribution of Python
```sh
wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash Anaconda3-2022.05-Linux-x86_64.sh
```

#### Step 2: Update existing packages

```sh
sudo apt update
```

#### Step 3: Install Docker and Docker Compose
Follow the instructions here:
[install-using-the-repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)  
Set up Docker's apt repository.
```sh
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
Install the Docker packages.
```sh
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
To run docker without `sudo`:

```sh
sudo groupadd docker
sudo usermod -aG docker $USER
```

#### Step 4: Run Docker

```sh
docker run hello-world
```

If you get `docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/create": dial unix /var/run/docker.sock: connect: permission denied.` error, restart your VM instance, or run:
`sudo dockerd`

**Note**: If you get `It is required that your private key files are NOT accessible by others. This private key will be ignored.` error, you should change permits on the downloaded file to protect your private key:

 ```sh
chmod 400 name-of-your-private-key-file.pem
```


### 1.2.3 Using installers

A simpler option consists of installing [Anaconda](https://www.anaconda.com/download) and [Docker Desktop](https://docs.docker.com/desktop/) using their web installers. To follow the program using **Python 3.9.7**, we can install a conda environment with the following command:
```sh
conda create -n mlops-zoomcamp python=3.9.7
```

We activate it with:
```sh
conda activate mlops-zoomcamp
```

To install necessary packages and tools:
```sh
conda install numpy pandas scikit-learn seaborn jupyter
```

## 1.3 Training a ride duration prediction model

**Note**: The NYC taxi data is now in parquet format, not CSV. You can download it using the command:
```sh
# For January
curl -O https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2021-01.parquet
# For February
curl -O "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2021-02.parquet"
```
If needed, install `pyarrow` or `fastparquet`:
```sh
pip install pyarrow
```
The advantage of parquet files is that they are smaller in size.

We trained our model using a [jupyter notebook](notebooks/duration-prediction.ipynb).


## 1.4 Course overview
From the training [notebook](notebooks/duration-prediction.ipynb), a couple of things can be improved. Notebooks are often intended for experiments. We need to make sure they are cleaned and more modular: maybe turned even into a python script.
Doing experiments in notebooks without being organized enough can make us lose the track of those experiments. We can use the *markdown* to keep notes of what happened: metrics and parameters for example. We can even save them into excel files. A better approach is logging all the metrics to an experiment-tracker. We will then be able to log it in other to check models performance. Models also can be saved to model registry so to keep all models with their metrics so to make sure we get the best model. For experiment tracking, we will use ml-flow on the following module. For continuing experiments with notebooks, we need to make sure to modify code, execute some cells and not some others. To turn the notebook in some steps that can be easily executable we can use ML pipelines. Steps can include:
- load & prepare data
- vectorize the dataframe
- train the model

  The pipeline can be parametrized in function of the data and the model we want to train. The output of the pipeline is a model that we want to deploy as a service for users. Once, the model is deployed, we need to make sure it is still performing well by monitoring it: if there is a performance drop re-execute the pipeline with new data for example, and deploy it again.
  Note that best practces include automating everything. For excluding completely humans from the process the model needs to be in a very mature model (highest level = 4).



## 1.5 MLOps maturity model

![ML Ops maturity model levels](../images/maturity_levels.jpg)

[Microsoft documentation](https://docs.microsoft.com/en-us/azure/architecture/example-scenario/mlops/mlops-maturity-model) defines five levels of maturity model:
- Level 0: No ML Ops automation at all.
Here we use jupyter notebooks for machine learning without proper pipelining, experiment tracking or metadata. When data scientists work alone, this usually happens. It's okay for some experimentations (POC LEVEL) but to pass the POC level we need more automation.
- Level 1: DevOps, No MLOps.
There is some level of automation. Releases are automated and models can be deployed in the same way as web services in usual software engineering. There is unit test, integration test, CI/CD, operation metrics but systems are not specific to Machine leraning at all. It is not easy to reproduce models. Here we left the POC level for going to production.
- Level 2: Automated Training.
There is ML training pipeline, experiment tracking and model registry (knowing which model is in production or not). The deployment is relatively simple, not necessarily automated - low friction deployment. We should considere it when we have 2 or 3+ cases or models.
- Level 3: Automated Deployment.
After the model is trained, how to easily deploy it. We often have an ML platform (a place to deploy models). The user can then make API call to access the model. Here we also have A/B test that can be ran from ML platforms to be able to test different versions of models and decide which is better. Model are often monitored as part of the deployment.
- Level 4: Full MLOps Automated Operations.
Models are automatically trained, retrained, deployed and monitored in one place.

NB: Even in mature organizations, not all services need to be at level 4. Do not rush. Choose what you need in function of your goal. 


## 1.6 Homework

---
