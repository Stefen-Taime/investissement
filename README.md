## Build PySpark & Delta Lake Financial Market Data ETL Workflow With Jenkins CICD

![](https://cdn-images-1.medium.com/max/2346/1*E5x0rf2Fnyz5MgM8Ast6cA.png)

ETL Process:

![](https://cdn-images-1.medium.com/max/3214/1*FeFC80C7gIjGXh3RhjTlHg.png)

1.  Extraction (Bronze Layer): The process starts with extracting CSV
    data files corresponding to various stock tickers. Using PySpark,
    the script reads these files, enforces a schema to maintain data
    integrity, and stores this raw data in a Delta table known as the
    'Bronze' layer.

2.  Transformation (Silver Layer): The transformation phase involves
    cleaning and restructuring the data. This step includes type casting
    and aggregation of financial metrics such as high, low, opening, and
    closing prices, as well as volume traded. The resultant structured
    data is saved in another Delta table, termed the 'Silver' layer.
    This layer serves two purposes: storing individual asset performance
    and market trend analysis.

3.  Load (Gold Layer): The final phase involves creating the 'Gold'
    layer, where the data is further refined for high-level analysis.
    This includes calculating the average return on investment (ROI) and
    volatility for each stock, segmented by year and month. The Gold
    layer represents the most valuable and insightful data, ready for
    in-depth analysis and decision-making processes.

    from pyspark.sql import SparkSession from pyspark.sql.functions
    import col, max, min, first, last, sum, avg, lit, stddev, to_date,
    year, month from pyspark.sql.types import StructType, StructField,
    DecimalType, LongType, DateType from datetime import datetime from
    typing import Optional

    class StandardETL: def **init**(self, storage_path: Optional\[str\]
    = None, database: Optional\[str\] = None, partition: Optional\[str\]
    = None): self.STORAGE_PATH = storage_path or
    's3a://investment/delta' self.DATABASE = database or 'investment'
    self.DEFAULT_PARTITION = partition or
    datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    spark =
    SparkSession.builder.appName("investment_pipelines").config("spark.sql.ansi.enabled",
    "false").enableHiveSupport().getOrCreate() etl = StandardETL()

    def load_csv_to_bronze(spark, file_name, table_name, ticker):
    file_path = f"/opt/spark/work-dir/investment/pipelines/{file_name}"
    schema = StructType(\[ StructField("Date", DateType(), True),
    StructField("Open", DecimalType(38, 10), True), StructField("High",
    DecimalType(38, 10), True), StructField("Low", DecimalType(38, 10),
    True), StructField("Close", DecimalType(38, 10), True),
    StructField("AdjClose", DecimalType(38, 10), True),
    StructField("Volume", LongType(), True) \])

        df = spark.read.csv(file_path, header=True, schema=schema)
        df = df.withColumn("Ticker", lit(ticker))
        # Debugging: Print the DataFrame schema
        df.printSchema()
        # Debugging: Show sample data
        df.show(5)
        # Write DataFrame to Bronze table
        df.write.format("delta").mode("overwrite").saveAsTable(table_name)

    def transform_to_silver(spark, bronze_table, asset_silver_table,
    market_silver_table): bronze_df = spark.table(bronze_table)

        converted_df = bronze_df.withColumn("Open", col("Open").cast(DecimalType(38, 10))) \
                            .withColumn("High", col("High").cast(DecimalType(38, 10))) \
                            .withColumn("Low", col("Low").cast(DecimalType(38, 10))) \
                            .withColumn("Close", col("Close").cast(DecimalType(38, 10)))

        asset_df = converted_df.groupBy("Date", "Ticker").agg(
            max("High").alias("HighPrice"),
            min("Low").alias("LowPrice"),
            first("Open").alias("OpeningPrice"),
            last("Close").alias("ClosingPrice"),
            avg("Volume").cast("long").alias("AverageVolume")
        ).withColumn("IsActive", lit(True))\
         .withColumn("Version", lit(1))\
         .withColumn("ValidFrom", col("Date"))\
         .withColumn("ValidTo", to_date(lit("2099-01-01"), "yyyy-MM-dd"))
        asset_df.write.format("delta").option("mergeSchema", "true").mode("overwrite").saveAsTable(asset_silver_table)

        market_df = converted_df.groupBy("Date", "Ticker").agg(
            sum("Volume").alias("TotalMarketVolume"),
            avg("Open").cast(DecimalType(38, 10)).alias("MarketOpening"),
            avg("Close").cast(DecimalType(38, 10)).alias("MarketClosing"),
            max("High").cast(DecimalType(38, 10)).alias("MarketHigh"),
            min("Low").cast(DecimalType(38, 10)).alias("MarketLow")
        ).withColumn("IsActive", lit(True))\
         .withColumn("Version", lit(1))\
         .withColumn("ValidFrom", col("Date"))\
         .withColumn("ValidTo", to_date(lit("2099-01-01"), "yyyy-MM-dd"))
        market_df.write.format("delta").option("mergeSchema", "true").mode("overwrite").saveAsTable(market_silver_table)

    def create_gold_layer(spark, asset_silver_table, gold_table):
    asset_df = spark.table(asset_silver_table) asset_df =
    asset_df.withColumn("Year", year("Date")).withColumn("Month",
    month("Date")) gold_df = asset_df.groupBy("Year", "Month",
    "Ticker").agg( avg("ClosingPrice").cast(DecimalType(38,
    10)).alias("AverageROI"),
    stddev("ClosingPrice").cast(DecimalType(38, 10)).alias("Volatility")
    )

        gold_df.write.format("delta").option("mergeSchema", "true").mode("overwrite").saveAsTable(gold_table)

    csv_files_and_tickers = { "AAPL.csv": "AAPL", "AMZN.csv": "AMZN",
    "GOOG.csv": "GOOG", "MSFT.csv": "MSFT", "ORCL.csv": "ORCL" }

    # Debugging: Print the types of the keys and values in the dictionary

    for file_name, ticker in csv_files_and_tickers.items():
    print(f"File: {file_name} (Type: {type(file_name)}), Ticker:
    {ticker} (Type: {type(ticker)})")

    for file_name, ticker in csv_files_and_tickers.items():
    load_csv_to_bronze(spark, file_name,
    f"{etl.DATABASE}.StockQuotesBronze", ticker)

    transform_to_silver(spark, f"{etl.DATABASE}.StockQuotesBronze",
    f"{etl.DATABASE}.AssetPerformanceSilver",
    f"{etl.DATABASE}.MarketTrendAnalysisSilver")
    create_gold_layer(spark, f"{etl.DATABASE}.AssetPerformanceSilver",
    f"{etl.DATABASE}.AssetPerformanceSummaryGold")

    spark.stop()

Technology Stack:

-   PySpark: Utilized for its powerful in-memory data processing
    capabilities, which are essential for handling large datasets
    typically found in financial markets.

-   Delta Lake: Chosen for its ACID transaction support and time-travel
    features, enabling reliable and consistent data storage and
    retrieval.

Pipeline Stages CICD:

![](https://cdn-images-1.medium.com/max/3194/1*WM28jPhRZy79TvEZabxDDQ.png)

1.  Initialization: Sets the groundwork for the pipeline execution,
    including environment variable setup.

2.  Clone Repo: Retrieves the project source code from the specified
    GitHub repository.

3.  Tests: Verifies the presence of essential CSV files, crucial for the
    investment analysis. This step ensures data integrity before
    proceeding further.

4.  Prepare Artifact: Compiles the necessary components of the project
    into a compressed file. This artifact represents the build which
    will be deployed.

5.  Upload to MinIO: Securely transfers the prepared artifact to MinIO
    for storage, ensuring that the build is available for deployment.

6.  Checkout Main Branch: Switches to the main branch in the repository,
    preparing it for the integration of new features or updates.

7.  Merge Feature into Main: Merges the feature branch into the main
    branch, combining new developments into the primary codebase.

8.  Deployment: Represents the stage where the application would be
    deployed, although specific deployment steps would depend on the
    project requirements.

![](https://cdn-images-1.medium.com/max/3826/1*ZDVB4GUlEkKsdRGUBm4n7g.png)

1.  Creating a New Branch on GitHub: When a developer wants to add a new
    feature, they start by creating a new branch on GitHub. This branch
    is often named according to the feature, for example,
    feature/01/buildRacineProject.

2.  Pushing Code and Triggering the Jenkins Pipeline: After developing
    the feature and pushing their code to the GitHub branch, a Jenkins
    pipeline is triggered. This pipeline is defined in a Jenkinsfile and
    follows several stages:

-   Initialization: The pipeline starts, displaying a start-up message.

-   Cloning the Repository: Jenkins clones the repository from GitHub
    using the specified credentials and branch.

-   Tests: Scripts are run to check for the presence of necessary files
    (such as CSV files) and other tests.

-   Preparing the Artifact: A folder is created to store the artifact,
    which is then compressed into a .tar.gz format.

-   Uploading to MinIO: The artifact is uploaded to MinIO, an object
    storage service, using specified credentials.

-   Merging with the Main Branch: After passing all the previous stages,
    the feature branch is merged with the main branch of GitHub.

-   Deployment: Once the merge is successful, the deployment of the
    application can begin.

-   Post-Process: After the pipeline, there are steps for cleanup and
    feedback depending on whether the build was a success or a failure.

## Starting Up the Infrastructure:

-   Command: make up

-   Action: This command navigates to the infra directory and starts the
    Docker containers using docker compose up. The --build flag ensures
    that the Docker images are built, and -d runs the containers in
    detached mode.

Creating Bronze Tables:

-   Command: make create-bronze-table

-   Action: Executes a Docker command to run a Spark job inside the
    local-spark container. This job runs a script (BronzeTables.py) that
    creates Bronze tables in your data architecture, handling initial
    data loading and raw data storage.

Creating Silver Tables:

-   Command: make create-silver-table

-   Action: Similar to the Bronze tables, this command runs the
    SilverTables.py script inside the local-spark container. The Silver
    tables represent an intermediate layer where data is cleaned and
    transformed.

Creating Gold Tables:

-   Command: make create-gold-table

-   Action: This command runs the GoldTables.py script. Gold tables are
    typically the final layer in a data pipeline, containing refined,
    business-level data ready for analysis and decision-making.

Running ETL Processes:

-   Command: make run-etl

-   Action: Executes the ETL (Extract, Transform, Load) process by
    running the investment_etl.py script in the local-spark container.
    This script handles the entire ETL process, transforming and loading
    data into the respective tables.

Starting the API Server:

-   Command: make api

-   Action: Navigates to the api directory and starts the Python API
    server by running main.py. This server handles API requests for your
    application.

Launching the Dashboard:

-   Command: make dashboard

-   Action: Moves into the dashboard directory and starts a simple HTTP
    server using Python. This server hosts your application's dashboard
    for data visualization and user interaction.

All-In-One Command:

-   Command: make all

-   Action: Sequentially executes the commands to create Bronze, Silver,
    and Gold tables, followed by running the ETL process. This is a
    comprehensive command that sets up the entire data pipeline.

[\*\*Github](https://github.com/Stefen-Taime/investissement)\*\*
