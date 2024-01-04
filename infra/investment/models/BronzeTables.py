from pyspark.sql import SparkSession

def create_tables(
    spark,
    path="s3a://investment/delta",
    database: str = "investment",
):
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

    # Drop the existing table if it exists
    spark.sql(f"DROP TABLE IF EXISTS {database}.StockQuotesBronze")

    # Create the new StockQuotesBronze table
    spark.sql(
        f"""
           CREATE TABLE {database}.StockQuotesBronze (
                    Date DATE,
                    Ticker STRING,
                    Open DECIMAL(38, 10),
                    High DECIMAL(38, 10),
                    Low DECIMAL(38, 10),
                    Close DECIMAL(38, 10),
                    AdjClose DECIMAL(38, 10),
                    Volume BIGINT
                ) USING DELTA
                PARTITIONED BY (Date)
                LOCATION '{path}/StockQuotesBronze';
            """
    )

def drop_tables(
    spark,
    database: str = "investment",
):
    # Drop the StockQuotesBronze table and the database
    spark.sql(f"DROP TABLE IF EXISTS {database}.StockQuotesBronze")
    spark.sql(f"DROP DATABASE IF EXISTS {database}")

if __name__ == '__main__':
    # Initialize Spark Session
    spark = (
        SparkSession.builder.appName("investment_models")
        .config("spark.executor.cores", "1")
        .config("spark.executor.instances", "1")
        .enableHiveSupport()
        .getOrCreate()
    )

    # Create tables
    create_tables(spark)
