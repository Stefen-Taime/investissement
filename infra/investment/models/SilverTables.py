from pyspark.sql import SparkSession

def create_tables(
    spark,
    path: str = "s3a://investment/delta",
    database: str = "investment",
):
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

    # Asset Performance Table (Silver Layer)
    spark.sql(f"DROP TABLE IF EXISTS {database}.AssetPerformanceSilver")
    spark.sql(
            f"""
            CREATE TABLE {database}.AssetPerformanceSilver (
                Date DATE,
                Ticker STRING,
                OpeningPrice DECIMAL(38, 10),
                ClosingPrice DECIMAL(38, 10),
                HighPrice DECIMAL(38, 10),
                LowPrice DECIMAL(38, 10),
                AverageVolume BIGINT,
                IsActive BOOLEAN,
                Version INT,
                ValidFrom DATE,
                ValidTo DATE
            ) USING DELTA
            LOCATION '{path}/AssetPerformanceSilver';
        """
    )

    # Market Trend Analysis Table (Silver Layer)
    spark.sql(f"DROP TABLE IF EXISTS {database}.MarketTrendAnalysisSilver")
    spark.sql(
        f"""
        CREATE TABLE {database}.MarketTrendAnalysisSilver (
            Date DATE,
            Ticker STRING,
            TotalMarketVolume BIGINT,
            MarketOpening DECIMAL(38, 10),
            MarketClosing DECIMAL(38, 10),
            MarketHigh DECIMAL(38, 10),
            MarketLow DECIMAL(38, 10),
            IsActive BOOLEAN,
            Version INT,
            ValidFrom DATE,
            ValidTo DATE
        ) USING DELTA
        LOCATION '{path}/MarketTrendAnalysisSilver'
        """
    )


def drop_tables(
    spark,
    database: str = "investment",
):
    spark.sql(f"DROP TABLE IF EXISTS {database}.AssetPerformanceSilver")
    spark.sql(f"DROP TABLE IF EXISTS {database}.MarketTrendAnalysisSilver")
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
