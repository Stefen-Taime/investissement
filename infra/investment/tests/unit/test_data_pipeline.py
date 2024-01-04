# Assuming you have a similar structure for your ETL processes
from investment.pipelines.investment_etl import InvestmentETL

class TestInvestmentETL:
    def test_get_bronze_datasets(self, spark) -> None:
        # Initialize your ETL process
        etl = InvestmentETL()

        # Get the datasets processed at the Bronze layer
        bronze_datasets = etl.get_bronze_datasets(spark, partition="YYYY-MM-DD_HH")

        # Test the number of datasets and their keys
        assert len(bronze_datasets) == expected_number
        assert sorted(bronze_datasets.keys()) == expected_datasets_keys

        # Validate the content of a specific dataset
        # Example: Check the row count of the 'stock_quotes' dataset
        assert bronze_datasets['stock_quotes'].curr_data.count() == expected_row_count

    def test_transform_to_silver_layer(self, spark) -> None:
        # Assuming you have a method to process Bronze data and transform it to Silver
        etl = InvestmentETL()
        silver_data = etl.transform_to_silver(spark)

        # Perform validations on the Silver data
        # Example: Validate schema, row count, specific data values, etc.
        pass

    def test_aggregate_to_gold_layer(self, spark) -> None:
        # Assuming you have a method to aggregate Silver data into Gold
        etl = InvestmentETL()
        gold_data = etl.aggregate_to_gold(spark)

        # Perform validations on the Gold data
        # Example: Validate KPIs, data aggregations, etc.
        pass

    # Add more tests as needed for specific transformations and aggregations
