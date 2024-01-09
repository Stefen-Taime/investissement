## Build PySpark & Delta Lake Financial Market Data ETL Workflow With Jenkins CICD

![](https://cdn-images-1.medium.com/max/2346/1*E5x0rf2Fnyz5MgM8Ast6cA.png)

ETL Process:

![](https://cdn-images-1.medium.com/max/3214/1*FeFC80C7gIjGXh3RhjTlHg.png)

### Extraction (Bronze Layer)

- **Description**: The process starts with extracting CSV data files corresponding to various stock tickers. Using PySpark, the script reads these files, enforces a schema to maintain data integrity, and stores this raw data in a Delta table known as the 'Bronze' layer.

### Transformation (Silver Layer)

- **Description**: The transformation phase involves cleaning and restructuring the data. This includes type casting and aggregating financial metrics such as high, low, opening, and closing prices, as well as volume traded. The resultant structured data is saved in another Delta table, termed the 'Silver' layer. This layer serves two purposes: storing individual asset performance and aiding in market trend analysis.

### Load (Gold Layer)

- **Description**: The final phase involves creating the 'Gold' layer, where the data is further refined for high-level analysis. This includes calculating the average return on investment (ROI) and volatility for each stock, segmented by year and month. The Gold layer represents the most valuable and insightful data, ready for in-depth analysis and decision-making processes.

## Technology Stack

- **PySpark**: Utilized for its powerful in-memory data processing capabilities, essential for handling large datasets typically found in financial markets.

- **Delta Lake**: Chosen for its ACID transaction support and time-travel features, enabling reliable and consistent data storage and retrieval.
# CI/CD Pipeline Stages

## Pipeline Stages

### Initialization
- **Description**: Sets the groundwork for the pipeline execution, including environment variable setup.

### Clone Repo
- **Description**: Retrieves the project source code from the specified GitHub repository.

### Tests
- **Description**: Verifies the presence of essential CSV files, crucial for the investment analysis. This step ensures data integrity before proceeding further.

### Prepare Artifact
- **Description**: Compiles the necessary components of the project into a compressed file. This artifact represents the build which will be deployed.

### Upload to MinIO
- **Description**: Securely transfers the prepared artifact to MinIO for storage, ensuring that the build is available for deployment.

### Checkout Main Branch
- **Description**: Switches to the main branch in the repository, preparing it for the integration of new features or updates.

### Merge Feature into Main
- **Description**: Merges the feature branch into the main branch, combining new developments into the primary codebase.

### Deployment
- **Description**: Represents the stage where the application would be deployed, although specific deployment steps would depend on the project requirements.

![CI/CD Pipeline Overview](https://cdn-images-1.medium.com/max/3194/1*WM28jPhRZy79TvEZabxDDQ.png)

## Process of Adding New Features

### Creating a New Branch on GitHub
- **Description**: When a developer wants to add a new feature, they start by creating a new branch on GitHub, often named according to the feature, e.g., `feature/01/buildRacineProject`.

### Pushing Code and Triggering the Jenkins Pipeline
- **Description**: After developing the feature and pushing their code to the GitHub branch, a Jenkins pipeline is triggered. This pipeline follows several stages:
  - **Initialization**: Displays a start-up message.
  - **Cloning the Repository**: Jenkins clones the repository from GitHub.
  - **Tests**: Runs scripts to check for the presence of necessary files and other tests.
  - **Preparing the Artifact**: Creates a folder for the artifact, which is then compressed.
  - **Uploading to MinIO**: The artifact is uploaded to MinIO, an object storage service.
  - **Merging with the Main Branch**: The feature branch is merged with the main branch of GitHub.
  - **Deployment**: Begins the deployment of the application.
  - **Post-Process**: Cleanup and feedback steps post-pipeline, depending on the build success.

![Jenkins Pipeline Overview](https://cdn-images-1.medium.com/max/3826/1*ZDVB4GUlEkKsdRGUBm4n7g.png)


## Starting Docker Containers

- **Command**: `make up`
- **Action**: Navigates to the infra directory and starts the Docker containers using `docker-compose up`. The `--build` flag ensures that the Docker images are built. The `-d` flag runs the containers in detached mode.

## Creating Bronze Tables

- **Command**: `make create-bronze-table`
- **Action**: Executes a Docker command to run a Spark job inside the `local-spark` container. This job runs the `BronzeTables.py` script, creating Bronze tables in your data architecture for initial data loading and raw data storage.

## Creating Silver Tables

- **Command**: `make create-silver-table`
- **Action**: Similar to the Bronze tables, this command runs the `SilverTables.py` script inside the `local-spark` container. Silver tables represent an intermediate layer where data is cleaned and transformed.

## Creating Gold Tables

- **Command**: `make create-gold-table`
- **Action**: Runs the `GoldTables.py` script. Gold tables are typically the final layer in a data pipeline, containing refined, business-level data ready for analysis and decision-making.

## Running ETL Processes

- **Command**: `make run-etl`
- **Action**: Executes the ETL (Extract, Transform, Load) process by running the `investment_etl.py` script in the `local-spark` container. This script handles the entire ETL process, transforming and loading data into the respective tables.

## Starting the API Server

- **Command**: `make api`
- **Action**: Navigates to the API directory and starts the Python API server by running `main.py`. This server handles API requests for your application.

## Launching the Dashboard

- **Command**: `make dashboard`
- **Action**: Moves into the dashboard directory and starts a simple HTTP server using Python. This server hosts your application's dashboard for data visualization and user interaction.

## All-In-One Command

- **Command**: `make all`
- **Action**: Sequentially executes the commands to create Bronze, Silver, and Gold tables, followed by running the ETL process. This comprehensive command sets up the entire data pipeline.

