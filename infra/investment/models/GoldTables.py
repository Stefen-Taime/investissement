from pyspark.sql import SparkSession

def create_tables(
    spark,
    path="s3a://investment/delta",
    database: str = "investment",
):
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

    # Drop the existing Gold layer table if it exists
    spark.sql(f"DROP TABLE IF EXISTS {database}.AssetPerformanceSummaryGold")
    spark.sql(
        f"""
           CREATE TABLE {database}.AssetPerformanceSummaryGold (
                Year INT,
                Month INT,
                Ticker STRING,
                AverageROI DECIMAL(38, 10),
                Volatility DECIMAL(38, 10)
            ) USING DELTA
            LOCATION '{path}/AssetPerformanceSummaryGold';
        """
    )

def drop_tables(spark, database: str = "investment"):
    spark.sql(f"DROP TABLE IF EXISTS {database}.AssetPerformanceSummaryGold")
    spark.sql(f"DROP DATABASE IF EXISTS {database}")

if __name__ == '__main__':
    spark = (
        SparkSession.builder.appName("investment_models")
        .config("spark.executor.cores", "1")
        .config("spark.executor.instances", "1")
        .enableHiveSupport()
        .getOrCreate()
    )
    create_tables(spark)
