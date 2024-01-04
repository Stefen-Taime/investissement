from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max, min, first, last, sum, avg, lit, stddev, to_date, year, month
from pyspark.sql.types import StructType, StructField, DecimalType, LongType, DateType
from datetime import datetime
from typing import Optional

class StandardETL:
    def __init__(self, storage_path: Optional[str] = None, database: Optional[str] = None, partition: Optional[str] = None):
        self.STORAGE_PATH = storage_path or 's3a://investment/delta'
        self.DATABASE = database or 'investment'
        self.DEFAULT_PARTITION = partition or datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

spark = SparkSession.builder.appName("investment_pipelines").config("spark.sql.ansi.enabled", "false").enableHiveSupport().getOrCreate()
etl = StandardETL()

def load_csv_to_bronze(spark, file_name, table_name, ticker):
    file_path = f"/opt/spark/work-dir/investment/pipelines/{file_name}"
    schema = StructType([
        StructField("Date", DateType(), True),
        StructField("Open", DecimalType(38, 10), True),
        StructField("High", DecimalType(38, 10), True),
        StructField("Low", DecimalType(38, 10), True),
        StructField("Close", DecimalType(38, 10), True),
        StructField("AdjClose", DecimalType(38, 10), True),
        StructField("Volume", LongType(), True)
    ])

    df = spark.read.csv(file_path, header=True, schema=schema)
    df = df.withColumn("Ticker", lit(ticker))

    # Debugging: Print the DataFrame schema
    df.printSchema()
    # Debugging: Show sample data
    df.show(5)
    
    # Write DataFrame to Bronze table
    df.write.format("delta").mode("overwrite").saveAsTable(table_name)
   

def transform_to_silver(spark, bronze_table, asset_silver_table, market_silver_table):
    bronze_df = spark.table(bronze_table)

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
    asset_df = spark.table(asset_silver_table)

    # Créer des colonnes pour l'année et le mois
    asset_df = asset_df.withColumn("Year", year("Date")).withColumn("Month", month("Date"))

    # Grouper par année, mois et Ticker
    gold_df = asset_df.groupBy("Year", "Month", "Ticker").agg(
        avg("ClosingPrice").cast(DecimalType(38, 10)).alias("AverageROI"),
        stddev("ClosingPrice").cast(DecimalType(38, 10)).alias("Volatility")
    )

    # Écrire dans la table Gold
    gold_df.write.format("delta").option("mergeSchema", "true").mode("overwrite").saveAsTable(gold_table)

csv_files_and_tickers = {
    "AAPL.csv": "AAPL",
    "AMZN.csv": "AMZN",
    "GOOG.csv": "GOOG",
    "MSFT.csv": "MSFT",
    "ORCL.csv": "ORCL"
}

# Debugging: Print the types of the keys and values in the dictionary
for file_name, ticker in csv_files_and_tickers.items():
    print(f"File: {file_name} (Type: {type(file_name)}), Ticker: {ticker} (Type: {type(ticker)})")

# Call the functions for ETL process
for file_name, ticker in csv_files_and_tickers.items():
    load_csv_to_bronze(spark, file_name, f"{etl.DATABASE}.StockQuotesBronze", ticker)

transform_to_silver(spark, f"{etl.DATABASE}.StockQuotesBronze", f"{etl.DATABASE}.AssetPerformanceSilver", f"{etl.DATABASE}.MarketTrendAnalysisSilver")
create_gold_layer(spark, f"{etl.DATABASE}.AssetPerformanceSilver", f"{etl.DATABASE}.AssetPerformanceSummaryGold")

# Close Spark session
spark.stop()