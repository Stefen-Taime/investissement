[

![Stefentaime](https://miro.medium.com/v2/resize:fill:88:88/1*ZvANyDda9Ual0g4Cq0RIug.jpeg)



](https://medium.com/@stefentaime_10958?source=post_page-----ad11c4efaf26--------------------------------)

![](https://miro.medium.com/v2/resize:fit:875/1*E5x0rf2Fnyz5MgM8Ast6cA.png)

ETL Process:

![](https://miro.medium.com/v2/resize:fit:1250/1*FeFC80C7gIjGXh3RhjTlHg.png)

1.  Extraction (Bronze Layer): The process starts with extracting CSV data files corresponding to various stock tickers. Using PySpark, the script reads these files, enforces a schema to maintain data integrity, and stores this raw data in a Delta table known as the ‘Bronze’ layer.
2.  Transformation (Silver Layer): The transformation phase involves cleaning and restructuring the data. This step includes type casting and aggregation of financial metrics such as high, low, opening, and closing prices, as well as volume traded. The resultant structured data is saved in another Delta table, termed the ‘Silver’ layer. This layer serves two purposes: storing individual asset performance and market trend analysis.
3.  Load (Gold Layer): The final phase involves creating the ‘Gold’ layer, where the data is further refined for high-level analysis. This includes calculating the average return on investment (ROI) and volatility for each stock, segmented by year and month. The Gold layer represents the most valuable and insightful data, ready for in-depth analysis and decision-making processes.

```
<span id="9e20" data-selectable-paragraph=""><span>from</span> pyspark.sql <span>import</span> SparkSession<br><span>from</span> pyspark.sql.functions <span>import</span> col, <span>max</span>, <span>min</span>, first, last, <span>sum</span>, avg, lit, stddev, to_date, year, month<br><span>from</span> pyspark.sql.types <span>import</span> StructType, StructField, DecimalType, LongType, DateType<br><span>from</span> datetime <span>import</span> datetime<br><span>from</span> typing <span>import</span> <span>Optional</span><br><br><span>class</span> <span>StandardETL</span>:<br>    <span>def</span> <span>__init__</span>(<span>self, storage_path: <span>Optional</span>[<span>str</span>] = <span>None</span>, database: <span>Optional</span>[<span>str</span>] = <span>None</span>, partition: <span>Optional</span>[<span>str</span>] = <span>None</span></span>):<br>        self.STORAGE_PATH = storage_path <span>or</span> <span>'s3a://investment/delta'</span><br>        self.DATABASE = database <span>or</span> <span>'investment'</span><br>        self.DEFAULT_PARTITION = partition <span>or</span> datetime.now().strftime(<span>"%Y-%m-%d-%H-%M-%S"</span>)<br><br>spark = SparkSession.builder.appName(<span>"investment_pipelines"</span>).config(<span>"spark.sql.ansi.enabled"</span>, <span>"false"</span>).enableHiveSupport().getOrCreate()<br>etl = StandardETL()<br><br><span>def</span> <span>load_csv_to_bronze</span>(<span>spark, file_name, table_name, ticker</span>):<br>    file_path = <span>f"/opt/spark/work-dir/investment/pipelines/<span>{file_name}</span>"</span><br>    schema = StructType([<br>        StructField(<span>"Date"</span>, DateType(), <span>True</span>),<br>        StructField(<span>"Open"</span>, DecimalType(<span>38</span>, <span>10</span>), <span>True</span>),<br>        StructField(<span>"High"</span>, DecimalType(<span>38</span>, <span>10</span>), <span>True</span>),<br>        StructField(<span>"Low"</span>, DecimalType(<span>38</span>, <span>10</span>), <span>True</span>),<br>        StructField(<span>"Close"</span>, DecimalType(<span>38</span>, <span>10</span>), <span>True</span>),<br>        StructField(<span>"AdjClose"</span>, DecimalType(<span>38</span>, <span>10</span>), <span>True</span>),<br>        StructField(<span>"Volume"</span>, LongType(), <span>True</span>)<br>    ])<br><br>    df = spark.read.csv(file_path, header=<span>True</span>, schema=schema)<br>    df = df.withColumn(<span>"Ticker"</span>, lit(ticker))<br>    <br>    df.printSchema()<br>    <br>    df.show(<span>5</span>)<br>    <br>    df.write.<span>format</span>(<span>"delta"</span>).mode(<span>"overwrite"</span>).saveAsTable(table_name)<br>   <br><span>def</span> <span>transform_to_silver</span>(<span>spark, bronze_table, asset_silver_table, market_silver_table</span>):<br>    bronze_df = spark.table(bronze_table)<br><br>    converted_df = bronze_df.withColumn(<span>"Open"</span>, col(<span>"Open"</span>).cast(DecimalType(<span>38</span>, <span>10</span>))) \<br>                        .withColumn(<span>"High"</span>, col(<span>"High"</span>).cast(DecimalType(<span>38</span>, <span>10</span>))) \<br>                        .withColumn(<span>"Low"</span>, col(<span>"Low"</span>).cast(DecimalType(<span>38</span>, <span>10</span>))) \<br>                        .withColumn(<span>"Close"</span>, col(<span>"Close"</span>).cast(DecimalType(<span>38</span>, <span>10</span>)))<br><br>    asset_df = converted_df.groupBy(<span>"Date"</span>, <span>"Ticker"</span>).agg(<br>        <span>max</span>(<span>"High"</span>).alias(<span>"HighPrice"</span>),<br>        <span>min</span>(<span>"Low"</span>).alias(<span>"LowPrice"</span>),<br>        first(<span>"Open"</span>).alias(<span>"OpeningPrice"</span>),<br>        last(<span>"Close"</span>).alias(<span>"ClosingPrice"</span>),<br>        avg(<span>"Volume"</span>).cast(<span>"long"</span>).alias(<span>"AverageVolume"</span>)<br>    ).withColumn(<span>"IsActive"</span>, lit(<span>True</span>))\<br>     .withColumn(<span>"Version"</span>, lit(<span>1</span>))\<br>     .withColumn(<span>"ValidFrom"</span>, col(<span>"Date"</span>))\<br>     .withColumn(<span>"ValidTo"</span>, to_date(lit(<span>"2099-01-01"</span>), <span>"yyyy-MM-dd"</span>))<br>    asset_df.write.<span>format</span>(<span>"delta"</span>).option(<span>"mergeSchema"</span>, <span>"true"</span>).mode(<span>"overwrite"</span>).saveAsTable(asset_silver_table)<br><br>    market_df = converted_df.groupBy(<span>"Date"</span>, <span>"Ticker"</span>).agg(<br>        <span>sum</span>(<span>"Volume"</span>).alias(<span>"TotalMarketVolume"</span>),<br>        avg(<span>"Open"</span>).cast(DecimalType(<span>38</span>, <span>10</span>)).alias(<span>"MarketOpening"</span>),<br>        avg(<span>"Close"</span>).cast(DecimalType(<span>38</span>, <span>10</span>)).alias(<span>"MarketClosing"</span>),<br>        <span>max</span>(<span>"High"</span>).cast(DecimalType(<span>38</span>, <span>10</span>)).alias(<span>"MarketHigh"</span>),<br>        <span>min</span>(<span>"Low"</span>).cast(DecimalType(<span>38</span>, <span>10</span>)).alias(<span>"MarketLow"</span>)<br>    ).withColumn(<span>"IsActive"</span>, lit(<span>True</span>))\<br>     .withColumn(<span>"Version"</span>, lit(<span>1</span>))\<br>     .withColumn(<span>"ValidFrom"</span>, col(<span>"Date"</span>))\<br>     .withColumn(<span>"ValidTo"</span>, to_date(lit(<span>"2099-01-01"</span>), <span>"yyyy-MM-dd"</span>))<br>    market_df.write.<span>format</span>(<span>"delta"</span>).option(<span>"mergeSchema"</span>, <span>"true"</span>).mode(<span>"overwrite"</span>).saveAsTable(market_silver_table)<br><br><span>def</span> <span>create_gold_layer</span>(<span>spark, asset_silver_table, gold_table</span>):<br>    asset_df = spark.table(asset_silver_table)<br>    asset_df = asset_df.withColumn(<span>"Year"</span>, year(<span>"Date"</span>)).withColumn(<span>"Month"</span>, month(<span>"Date"</span>))<br>    gold_df = asset_df.groupBy(<span>"Year"</span>, <span>"Month"</span>, <span>"Ticker"</span>).agg(<br>        avg(<span>"ClosingPrice"</span>).cast(DecimalType(<span>38</span>, <span>10</span>)).alias(<span>"AverageROI"</span>),<br>        stddev(<span>"ClosingPrice"</span>).cast(DecimalType(<span>38</span>, <span>10</span>)).alias(<span>"Volatility"</span>)<br>    )<br><br>    gold_df.write.<span>format</span>(<span>"delta"</span>).option(<span>"mergeSchema"</span>, <span>"true"</span>).mode(<span>"overwrite"</span>).saveAsTable(gold_table)<br><br>csv_files_and_tickers = {<br>    <span>"AAPL.csv"</span>: <span>"AAPL"</span>,<br>    <span>"AMZN.csv"</span>: <span>"AMZN"</span>,<br>    <span>"GOOG.csv"</span>: <span>"GOOG"</span>,<br>    <span>"MSFT.csv"</span>: <span>"MSFT"</span>,<br>    <span>"ORCL.csv"</span>: <span>"ORCL"</span><br>}<br><br><br><span>for</span> file_name, ticker <span>in</span> csv_files_and_tickers.items():<br>    <span>print</span>(<span>f"File: <span>{file_name}</span> (Type: <span>{<span>type</span>(file_name)}</span>), Ticker: <span>{ticker}</span> (Type: <span>{<span>type</span>(ticker)}</span>)"</span>)<br><br><span>for</span> file_name, ticker <span>in</span> csv_files_and_tickers.items():<br>    load_csv_to_bronze(spark, file_name, <span>f"<span>{etl.DATABASE}</span>.StockQuotesBronze"</span>, ticker)<br><br>transform_to_silver(spark, <span>f"<span>{etl.DATABASE}</span>.StockQuotesBronze"</span>, <span>f"<span>{etl.DATABASE}</span>.AssetPerformanceSilver"</span>, <span>f"<span>{etl.DATABASE}</span>.MarketTrendAnalysisSilver"</span>)<br>create_gold_layer(spark, <span>f"<span>{etl.DATABASE}</span>.AssetPerformanceSilver"</span>, <span>f"<span>{etl.DATABASE}</span>.AssetPerformanceSummaryGold"</span>)<br><br>spark.stop()</span>
```

Technology Stack:

-   PySpark: Utilized for its powerful in-memory data processing capabilities, which are essential for handling large datasets typically found in financial markets.
-   Delta Lake: Chosen for its ACID transaction support and time-travel features, enabling reliable and consistent data storage and retrieval.

Pipeline Stages CICD:

![](https://miro.medium.com/v2/resize:fit:1250/1*WM28jPhRZy79TvEZabxDDQ.png)

1.  Initialization: Sets the groundwork for the pipeline execution, including environment variable setup.
2.  Clone Repo: Retrieves the project source code from the specified GitHub repository.
3.  Tests: Verifies the presence of essential CSV files, crucial for the investment analysis. This step ensures data integrity before proceeding further.
4.  Prepare Artifact: Compiles the necessary components of the project into a compressed file. This artifact represents the build which will be deployed.
5.  Upload to MinIO: Securely transfers the prepared artifact to MinIO for storage, ensuring that the build is available for deployment.
6.  Checkout Main Branch: Switches to the main branch in the repository, preparing it for the integration of new features or updates.
7.  Merge Feature into Main: Merges the feature branch into the main branch, combining new developments into the primary codebase.
8.  Deployment: Represents the stage where the application would be deployed, although specific deployment steps would depend on the project requirements.

![](https://miro.medium.com/v2/resize:fit:1250/1*ZDVB4GUlEkKsdRGUBm4n7g.png)

1.  Creating a New Branch on GitHub: When a developer wants to add a new feature, they start by creating a new branch on GitHub. This branch is often named according to the feature, for example, `feature/01/buildRacineProject`.
2.  Pushing Code and Triggering the Jenkins Pipeline: After developing the feature and pushing their code to the GitHub branch, a Jenkins pipeline is triggered. This pipeline is defined in a `Jenkinsfile` and follows several stages:

-   Initialization: The pipeline starts, displaying a start-up message.
-   Cloning the Repository: Jenkins clones the repository from GitHub using the specified credentials and branch.
-   Tests: Scripts are run to check for the presence of necessary files (such as CSV files) and other tests.
-   Preparing the Artifact: A folder is created to store the artifact, which is then compressed into a `.tar.gz` format.
-   Uploading to MinIO: The artifact is uploaded to MinIO, an object storage service, using specified credentials.
-   Merging with the Main Branch: After passing all the previous stages, the feature branch is merged with the main branch of GitHub.
-   Deployment: Once the merge is successful, the deployment of the application can begin.
-   Post-Process: After the pipeline, there are steps for cleanup and feedback depending on whether the build was a success or a failure.

## Starting Up the Infrastructure:

-   Command: `make up`
-   Action: This command navigates to the `infra` directory and starts the Docker containers using `docker compose up`. The `--build` flag ensures that the Docker images are built, and `-d` runs the containers in detached mode.

Creating Bronze Tables:

-   Command: `make create-bronze-table`
-   Action: Executes a Docker command to run a Spark job inside the `local-spark` container. This job runs a script (`BronzeTables.py`) that creates Bronze tables in your data architecture, handling initial data loading and raw data storage.

Creating Silver Tables:

-   Command: `make create-silver-table`
-   Action: Similar to the Bronze tables, this command runs the `SilverTables.py` script inside the `local-spark` container. The Silver tables represent an intermediate layer where data is cleaned and transformed.

Creating Gold Tables:

-   Command: `make create-gold-table`
-   Action: This command runs the `GoldTables.py` script. Gold tables are typically the final layer in a data pipeline, containing refined, business-level data ready for analysis and decision-making.

Running ETL Processes:

-   Command: `make run-etl`
-   Action: Executes the ETL (Extract, Transform, Load) process by running the `investment_etl.py` script in the `local-spark` container. This script handles the entire ETL process, transforming and loading data into the respective tables.

Starting the API Server:

-   Command: `make api`
-   Action: Navigates to the `api` directory and starts the Python API server by running `main.py`. This server handles API requests for your application.

Launching the Dashboard:

-   Command: `make dashboard`
-   Action: Moves into the `dashboard` directory and starts a simple HTTP server using Python. This server hosts your application's dashboard for data visualization and user interaction.

All-In-One Command:

-   Command: `make all`
-   Action: Sequentially executes the commands to create Bronze, Silver, and Gold tables, followed by running the ETL process. This is a comprehensive command that sets up the entire data pipeline.

[**Github**](https://github.com/Stefen-Taime/investissement)