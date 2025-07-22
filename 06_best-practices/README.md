![MLOps Zoomcamp](../images/banner-2025.jpg)

# 🚀 MLOps Zoomcamp – Module 6: Best Practices
**Instructors:** Alexey Grigorev

---
# Plan
- [x] Testing the code: unit tests with pytest
- [x] Integration tests with docker-compose
- [x] Testing cloud services with LocalStack
- [x] Code quality: linting and formatting
- [x] Git pre-commit hooks
- [x] Makefiles and make
- [ ] Staging and production environments
- [ ] Infrastructure as Code
- [ ] CI/CD and GitHub Actions
---

# Part A
## 📌 6.1 Testing Python code with pytest
This module covers best practices for testing Python code, using an example from [Module 4](../04_deployment/) involving a streaming architecture with Lambda and Kinesis. 
![Streaming Architecture](../images/stream_archi.png)
This architecture included an events stream, a Lambda function processing events and getting a model from S3 or locally, and a predictions stream for output. Here we want to add **unit tests** and **integration tests** to the Lambda function code to improve its engineering quality.    

#### Setting up the Testing Environment
For that we will:
- Set our `pipenv` environment using [Pipfile](./notebooks/course/streaming/Pipfile): `pipenv install --python=3.9`.
> Note that for deleting the Pipenv environment, you should first delete the environment: `pipenv --rm` and then remove Pipfile files: `rm Pipfile*`.
- Create a `tests` folder to store test files: `mkdir tests`.
- Add a `__init__.py` file in the `tests` folder to let **python** know that it is a **Python package** and a [test file](./tests/model_test.py) for testing.
- Install the **pytest** library as a development dependency using `pipenv`: `pipenv install --dev pytest`. Note we only need that library for performing tests during the development. We do not need it for production.
> To check `pytest` version, you can run the command: `pipenv run pytest --version`.
- Configure Visual Studio Code to discover and run tests:
    - Check the Python extension and install it on SSH or restart if needed.
    - Use the shortcut `Command + Shift + P` and select the **correct Python interpreter** (the virtual environment): it is tagged with **Pipenv** and its path can be checked using the command `pipenv --venv`.
    - We can now configure Python tests using the tab on the left. Note that we will have to select the Python test framework `pytest` and specify the [tests](./notebooks/course/streaming/tests/) directory. 
    - A basic test like `assert 1 == 1` can be used to confirm pytest setup is working.         

#### Refactoring Code for Testability
Initially, attempting to import the original [`lambda_function.py`](../../../../04_deployment/notebooks/course/4.4_streaming/lambda_function.py) directly for testing fails because global variables (like the model loading logic) are executed upon import. In fact, the logic that requires external resources (like S3) is at the top level, making simple unit testing difficult. Hence the need to perform some refactoring. We will simplfy the original [lambda function](./lambda_function.py) so that it imports the [model from another script](./model.py). This way, we will define a model class for that script and will be able to perform [unit tests](./tests/model_test.py) for the methods of that model. This refactoring allows unit tests to import the `model.py` file without triggering the problematic global logic. Note that to handle external dependencies (put predictions into a Kinesis stream), we will create a **callback mechanism**. With the code refactory completed, Pytest works well. There are green checks to confirm that in the testing panel.

> Tests can also be run through the command line interface: `pipenv run pytest tests`.

We can now update our [Dockerfile](./Dockerfile) and build the model image:

```bash
docker build -t stream-model-duration:v2 .
```
then run it:
```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e MODEL_RUN_ID="1ca05c6d23f44066a4a4dcdbe1639de4" \
    -e TEST_RUN="True" \
    -e AWS_DEFAULT_REGION="us-east-1" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    stream-model-duration:v2
```
> Note that we need to pass credentials using the command line interface, before running the image:
```sh
AWS_ACCESS_KEY_ID="ID_123"
AWS_SECRET_ACCESS_KEY="Key_123"
```
To test our docker image, we can run a [test script](./notebooks/course/streaming/test_docker.py): `python test_docker.py`.

#### Unit Tests vs. Integration Tests
- **Unit tests** focus on testing small, isolated pieces of code (functions, methods). They are independent and fast.   
- **Integration tests** verify that different parts of the system work together correctly, potentially involving external services.    

| Test Type          | Scope                               | Dependencies               | Speed | Purpose                                   |
| :----------------- | :---------------------------------- | :------------------------- | :---- | :---------------------------------------- |
| **Unit Tests**     | Individual functions/methods        | Mocked/Isolated            | Fast  | Verify correctness of small code units    |
| **Integration Tests**| Multiple components working together | Real or simulated external | Slower| Verify system parts integrate correctly |


## 🛠️ 6.2 Integration tests with docker-compose
Previously, we refactored the Lambda function code to delegate core logic to a `model.py` file, making it easier to test individual components. We then implemented unit tests to cover specific functions within the `model.py` file, but their scope was limited to individual functions and did not verify the entire system's functionality or its ability to handle requests and responses. For testing the entire system, we initially run a docker image and a [testing script](./notebooks/course/streaming/test_docker.py). We will convert this script into a [**proper integration test**](./notebooks/course/streaming/integration-test/test_docker.py) by adding `assert` statements to compare actual and expected responses. To compare complex dictionary responses and identify specific differences, we will install the `deepdiff` library:
```sh
pipenv install --dev deepdiff
```
It can even be configured with a `significant_digits` tolerance for float comparisons.  

#### Managing Test Dependencies
Integration tests should ideally limit external dependencies to ensure reliability and offline execution. For this reason and also to avoid using S3 buckets, we earlier decided earlier to copy the [MLFlow artifact fodler](./notebooks/course/streaming/mlflow-models/) to the docker image instead of connecting to an s3 bucket. To facilitate local model loading in Docker, one can decide to download the model files from S3 to a local `model` folder within the `integration_test` directory:
```sh
aws s3 cp --recursive MODEL_REMOTE_LOCATION model
```
with `MODEL_REMOTE_LOCATION=s3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model` the remote address of the model.
Once done, we can **mount** this local `model` folder into the Docker container using the `-v` flag (`-v ./model:/app/model`), and setting the `MODEL_LOCATION` environment variable to the container's path (`/app/model`).

From the [integration test folder](./notebooks/course/streaming/integration-test/), we can build the model image:

```bash
docker build -t stream-model-duration:v2 ..
```
and then run it :
```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e MODEL_RUN_ID="1ca05c6d23f44066a4a4dcdbe1639de4" \
    -e MODEL_LOCATION="/app/model" \
    -e TEST_RUN="True" \
    -e AWS_DEFAULT_REGION="us-east-1" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -v $(pwd)/model:/app/model \
    stream-model-duration:v2
```
> Note that we need to pass credentials using the command line interface as done [previously](#-61-testing-python-code-with-pytest).

Finally, we can test the image:
```sh
pipenv run python test_docker.py
```


#### Automating Integration Tests with Docker Compose
The entire testing workflow, including building the Docker image, running the service, executing tests, and stopping the service, can be automated using a [shell script](./notebooks/course/streaming/integration-test/run.sh). The script ensures it always runs from its own directory using a specific bash command. Docker image tags are dynamically generated using the current date and time to ensure uniqueness. **Docker Compose**  is used to manage the service's configuration, including image name, exposed ports, environment variables (e.g., `MODEL_LOCATION`), and volume mounts for the local model folder.    

> For the automation to work, we neeed to update the credentials in the [docker-compose configuration file](./notebooks/course/streaming/integration-test/docker-compose.yaml) and also to make the script executable:
```sh
chmod +x run.sh
```
and run it:
```sh
bash run.sh
```

#### Handling Script Exit Codes for CI/CD
For Continuous Integration/Continuous Deployment (CI/CD) systems, a script's exit code determines job success (0) or failure (non-zero). Using `set -e` in a bash script forces it to exit immediately upon the first non-zero command, but this can prevent cleanup actions like `docker-compose down`. A more robust approach is to manually capture the test's exit code into a variable and then conditionally print Docker Compose logs and exit with the captured code after ensuring `docker-compose down` is executed. This ensures that if tests fail, the CI/CD job will be marked as failed, and relevant container logs will be available for debugging.   


## 📉 6.3 Testing Cloud Services with LocalStack
**LocalStack** is a fully functional local AWS cloud stack used for testing AWS services locally. After **Unit tests** to test individual functions with **Pytest**, **Integration tests** by running a service inside Docker and using a Python script to verify its output, we can proceed to test the **Kinesis connection**, specifically the part of the code that puts responses to a Kinesis stream.


#### LocalStack Installation and Configuration
LocalStack can be installed via pip:
```sh
pip install localstack
```
We can also use a **Docker Compose** configuration [file](./notebooks/course/streaming/integration-test/docker-compose.yaml). The `SERVICES` environment variable in the Docker Compose configuration can be set to `kinesis` to start only the Kinesis server, preventing other services from running .

#### Testing LocalStack with AWS CLI
To verify LocalStack functionality, we can start the Kinesis service using `docker compose up kinesis`. When using the **AWS CLI** to interact with LocalStack, we must specify the `endpoint-url` parameter, pointing to `http://localhost:4566`. For example,
`aws kinesis list-streams --endpoint-url http://localhost:4566` lists streams from LocalStack, not your actual AWS account. Streams can be created in LocalStack using commands like `aws kinesis create-stream --stream-name write-predictions --shard-count 1 --endpoint-url http://localhost:4566`. This ensures that streams are created locally within LocalStack and do not appear in your live AWS account.

To configure application code to use LocalStack, a special environmental variable, `KINESIS_ENDPOINT_URL`, can be created. Inside the Docker Compose network, services can refer to each other by their service names (e.g., `http://kinesis:4566`), while outside the network, `localhost` is used. 


#### Running and Verifying the Integration Test
For integration tests, the Kinesis stream needs to be created every time the test runs, which can be integrated into our [test script](./notebooks/course/streaming/integration-test/run.sh). Data in the Kinesis stream can be checked using the AWS CLI ensuring the `endpoint-url` is specified. For automated testing, a [Python script](./notebooks/course/streaming/integration-test/test_kinesis.py) using **Boto3** is recommended to interact with Kinesis. Note that in some cases, LocalStack might not require base64 decoding for records, allowing direct JSON parsing.

> Some [instructions](./notebooks/course/streaming/README.md) available for local testing with the AWS CLI.
> Note that in case of any code failure, our [script](./notebooks/course/streaming/integration-test/run.sh) was written to exit. To run it: `bash run.sh`.


## 🖥️ 6.4 Code Quality: linting and formatting
Code quality extends beyond reliability (covered by tests: the code does what it is expected) to include aesthetic aspects and adherence to best practices, aiming for "beautiful" code. [**PEP 8**](https://peps.python.org/pep-0008/) is a crucial style guide for Python, part of the **Python Enhancement Proposals (PEPs)**, which dictates how Python code should be formatted and structured.

### Linting with Pylint
**Linters** are tools that perform static code analysis to check if code follows conventions like PEP 8 and identify common mistakes or potentially harmful patterns (e.g., global variables). 

**Pylint** is a widely used static code analysis tool for Python that checks for style guide adherence and common coding issues. To install Pylint as a development dependency, use `pipenv install pylint --dev`. We can then run Pylint from the terminal using
```sh
pipenv run pylint .
```
for the current directory or:
```sh
pylint <file_name.py>
```
for a specific file.

This command outputs various **warnings and suggestions**, such as missing documentation for modules or functions, trailing whitespace, or issues with naming conventions, with a **note for the code**. Pylint can be integrated with IDEs like VS Code (an extension is available), where it underlines problems directly in the code editor, making issues easier to spot. Pylint's exit code is non-zero if warnings are present, which can be used to fail CI/CD jobs or pre-commit hooks, ensuring code quality before deployment.

Pylint's behavior can be configured to suppress specific warnings, either globally or locally. Global configuration can be done via a `.pylintrc` file or, preferably, using [pyproject.toml](./notebooks/course/streaming/pyproject.toml): a common configuration file for many Python projects. In `pyproject.toml`, warnings can be disabled under the `[tool.pylint.messages_control]` section by listing their codes in a `disable` array. This is a better option as other tools can use this configuration file. Locally, warnings can be disabled for specific code blocks (e.g., a class or function) by adding `# pylint: disable=<warning-code>` comments directly in the code.

Common issues addressed by Pylint include:
- Missing docstrings for modules, classes, or functions.
- "Too few public methods" in a class.
- Unused arguments in functions.
- "Line too long" warnings, which can often be resolved by refactoring long data lines into separate files or by adjusting formatting rules.
- Encoding issues, such as missing `encoding='utf-8'` for file operations, which can cause problems on different operating systems.

### Code Formatting with Black & Import Sorting with isort
We can install those tools with:
```sh
pipenv install --dev black isort
```

**Black** is an opinionated code formatter that automatically reformats Python code to a consistent style, improving aesthetics and readability. Black is highly opinionated. For example, it defaults to using double quotes for strings, though this can be configured. To prevent Black from changing string quotes, `skip-string-normalization = true` can be set in the `[tool.black]` section of [pyproject.toml](./notebooks/course/streaming/pyproject.toml). Other Black configurations in [pyproject.toml](./notebooks/course/streaming/pyproject.toml) include `target-version` (e.g., `3.9`) and `line-length` (e.g., `88`). To see the changes Black would make without applying them, use 
```sh
pipenv run black --diff .
```
To apply changes, use 
```sh
pipenv run black .
```
Adding a trailing comma to multi-line structures (e.g., lists, dictionaries, function arguments) can prevent Black from reformatting them into a single line.

**isort** is a dedicated tool for sorting imports in Python files, ensuring they are consistently ordered. It typically groups standard library imports, then third-party imports, and finally local application imports. To see the changes isort would make, use 
```sh
pipenv run isort --diff .
```
To apply changes, use
```sh
pipenv run isort .
```
isort can also be configured in `pyproject.toml` under the `[tool.isort]` section, allowing for different sorting profiles or custom rules.

### Integrated Code Quality Workflow
Code quality tools are typically used in a defined sequence as part of a development workflow, often before committing code to version control or within a CI/CD pipeline.
A common workflow involves running tools in the following order to ensure a clean and consistent codebase:
    1.  **isort**: Sorts imports.
    2.  **Black**: Formats the code.
    3.  **Pylint**: Lints the code for style and common errors.
    4.  **Pytest**: Runs tests to ensure functionality.
This sequential application helps ensure that formatting and import issues are resolved before linting and testing, streamlining the development process.


## 🧰 6.5 Git pre-commit hooks
Developers often use multiple commands for code quality, such as **isort** for sorting imports, **black** for formatting, **pylint** for linting, and **pytest** for running tests. It is easy to forget to execute these commands consistently before committing code to a Git repository. To prevent this, **Git pre-commit hooks** can be used to run checks automatically *before* the code is committed. Git provides various hooks, with `pre-commit` being the one executed prior to a commit.

#### The `pre-commit` Tool
The **`pre-commit`** tool is a Python-based utility that simplifies defining and managing these pre-commit scripts and hooks. It can be installed using `pip` or `pipenv`:
```sh
pipenv install --dev pre-commit
```
Git repositories contain a `.git/hooks` folder where a bash script named `pre-commit.sample` is placed to execute before every commit. The `pre-commit` tool helps update this script. The `.git` folder is local to each repository clone and is not committed; therefore, every team member must run `pre-commit install` once after cloning a repository to set up the hooks locally. For testing purposes within a larger repository, a specific subfolder can be initialized as a standalone Git repository using `git init` to enable `pre-commit` hooks for that isolated context.

#### Configuration and Usage
`pre-commit` requires a configuration file, typically `.pre-commit-config.yaml`, which can be generated as a sample and redirected into the file using:
```sh
pipenv run pre-commit sample-config > .pre-commit-config.yaml
```
The configuration file defines which hooks to run. Default hooks include checks for trailing white spaces, end-of-file issues, valid YAML syntax, and large files. After creating the config file, we create the actual Git hook script in `.git/hooks`:
```sh
pipenv run pre-commit install
```
When a user performs `git add` and `git commit`, the `pre-commit` hook automatically executes the configured checks. If any hook fails (e.g., due to formatting errors or failing tests), it will modify the problematic files (if applicable) and prevent the commit from completing. The user then needs to add the modified files (`git add`) and re-commit. A commit is only successful if all pre-commit hooks pass with a zero error code.

#### Integrating Custom Code Quality Tools
`pre-commit` supports integrating various external code quality tools beyond its built-in hooks (e.g., `check-json`, `detect-private-keys`). Tools like **isort**, **black**, **pylint**, and **pytest** can be added to the `.pre-commit-config.yaml` file by specifying their repository, revision (version), and hook ID. Alternatively, for tools like `pylint` and `pytest`, specific commands can be directly defined within the configuration, along with arguments (e.g., specifying a `tests` folder for `pytest`).

> Deliberately failing a test can confirm that the `pytest` hook correctly prevents the commit, demonstrating its effectiveness in maintaining code quality.

#### Benefits of Using Pre-Commit Hooks
`pre-commit` hooks automate the execution of code quality checks, significantly saving time by eliminating the need for manual execution. They ensure that code is properly formatted, linted, and tested *before* it enters the shared code repository, thereby enforcing good engineering practices. This automation means developers do not need to constantly remember to run these checks themselves, streamlining the development workflow. It is highly recommended to use `pre-commit` hooks for project development to maintain consistent code quality.


## 🧭 6.6 Makefiles and Make
**Make** is a tool used to define aliases and orchestrate commands through **Makefiles**. It is often pre-installed on Linux and Mac, and can be installed on Windows using package managers like Choco. You can check the version with:
```sh
make --version
```
A [Makefile](./notebooks/course/streaming/Makefile) is a file that specifies commands associated with targets (aliases). Commands in a Makefile are defined as **targets** (e.g., `run`), which execute specified actions when called. (e.g., `make run`). Makefiles allow defining **dependencies**, where one target must complete successfully before another can run (e.g., `run` can depends on `test`). This can help creating a **directed acyclic graph (DAG)** of dependencies, ensuring tasks are executed in the correct order, a bit like an orchestrator. For example, a `build` target can depend on `test` and `integration_test` targets.

#### Practical Applications
Makefiles are useful for automating various development tasks:
- **Quality Checks**: Running linters (e.g., pylint) and formatters (e.g., black, isort) before other steps.
```sh
pipenv run make quality_checks
```
 - **Testing**: Executing unit tests (e.g., `pytest`) and integration tests.  
```sh
pipenv run make test
pipenv run make integration_test
```
- **Build Automation**: Orchestrating complex builds, such as Docker image creation using `docker compose`.
```sh
pipenv run make build
```
- **Publishing**: Automating deployment steps, like publishing an image to ECR, ensuring dependent build and test steps are completed first.
```sh
pipenv run make publish
```
A common setup target can be defined to prepare the development environment and install pre-commit hooks, simplifying project onboarding:
```sh
make setup
```

> Variables can be passed to scripts, allowing conditional logic within those scripts to avoid redundant operations (e.g., checking if an image is already built before rebuilding). When using variables in Makefiles, direct expansion `$(VAR)` might not execute shell commands within the variable value, leading to unexpected results. To ensure shell commands within variables are evaluated, use the `shell` keyword (e.g., `$(shell command)`).

Makefiles offer significant advantages for project management and automation:
    - **Convenience**: Eliminates the need to remember complex, multi-step commands.
    - **Orchestration**: Manages dependencies between tasks, ensuring correct execution order.
    - **Auto-completion**: Provides tab auto-completion for defined targets, improving usability.
    - **Standardization**: Centralizes project setup and common operations, making it easier for new contributors to get started.

## 📝 6.7 Homework
Homework for this module is available [here.](notebooks/homework/homework_06.ipynb).

---   

# Part B

### Infrastructure-as-Code
with Terraform 

![image](../images/AWS-stream-pipeline.png)

#### Summary
* Setting up a stream-based pipeline infrastructure in AWS, using Terraform
* Project infrastructure modules (AWS): Kinesis Streams (Producer & Consumer), Lambda (Serving API), S3 Bucket (Model artifacts), ECR (Image Registry)

Further info here:
* [Concepts of IaC and Terraform](docs.md#concepts-of-iac-and-terraform)
* [Setup and Execution](https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/06-best-practices/code#iac)

#### 6B.1: Terraform - Introduction

https://www.youtube.com/watch?v=zRcLgT7Qnio&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=48

* Introduction
* Setup & Pre-Reqs
* Concepts of Terraform and IaC (reference material from previous courses)

#### 6B.2: Terraform - Modules and Outputs variables

https://www.youtube.com/watch?v=-6scXrFcPNk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=49

* What are they?
* Creating a Kinesis module

#### 6B.3: Build an e2e workflow for Ride Predictions

https://www.youtube.com/watch?v=JVydd1K6R7M&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=50

* TF resources for ECR, Lambda, S3

#### 6B.4: Test the pipeline e2e

https://www.youtube.com/watch?v=YWao0rnqVoI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=51

* Demo: apply TF to our use-case, manually deploy data dependencies & test
* Recap: IaC, Terraform, next steps

Additional material on understanding Terraform concepts here: [Reference Material](docs.md#concepts-of-iac-and-terraform)

<br>

### CI/CD
with GitHub Actions

![image](ci_cd_zoomcamp.png)

#### Summary

* Automate a complete CI/CD pipeline using GitHub Actions to automatically trigger jobs 
to build, test, and deploy our service to Lambda for every new commit/code change to our repository.
* The goal of our CI/CD pipeline is to execute tests, build and push container image to a registry,
and update our lambda service for every commit to the GitHub repository.

Further info here: [Concepts of CI/CD and GitHub Actions](docs.md#concepts-of-ci-cd-and-github-actions)


#### 6B.5: CI/CD - Introduction

https://www.youtube.com/watch?v=OMwwZ0Z_cdk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=52

* Architecture (Ride Predictions)
* What are GitHub Workflows?

#### 6B.6: Continuous Integration

https://www.youtube.com/watch?v=xkTWF9c33mU&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=53

* `ci-tests.yml`
    * Automate sections from tests: Env setup, Unit test, Integration test, Terraform plan
    * Create a CI workflow to trigger on `pull-request` to `develop` branch
    * Execute demo

#### 6B.7: Continuous Delivery

https://www.youtube.com/watch?v=jCNxqXCKh2s&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=54

* `cd-deploy.yml`
    * Automate sections from tests: Terraform plan, Terraform apply, Docker build & ECR push, Update Lambda config
    * Create a CD workflow to trigger on `push` to `develop` branch
    * Execute demo

#### Alternative CICD Solutions

* Using args and env variables in docker image, and leveraging makefile commands in cicd
    * Check the repo [README](https://github.com/Nakulbajaj101/mlops-zoomcamp/blob/main/06-best-practices/code-practice/README.md)
    * Using the args [Dockerfile](https://github.com/Nakulbajaj101/mlops-zoomcamp/blob/main/06-best-practices/code-practice/Dockerfile)
    * Using build args [ECR terraform](https://github.com/Nakulbajaj101/mlops-zoomcamp/blob/main/06-best-practices/code-practice/deploy/modules/ecr/main.tf)
    * Updating lambda env variables [Post deploy](https://github.com/Nakulbajaj101/mlops-zoomcamp/blob/main/06-best-practices/code-practice/deploy/run_apply_local.sh)
    * Making use of make file commands in CICD [CICD](https://github.com/Nakulbajaj101/mlops-zoomcamp/tree/main/.github/workflows)
