from pyspark.sql import SparkSession


def read_transformed_data(spark, output_transformed):
    # Read raw data into a DataFrame
    df = spark.read.parquet(output_transformed, header=True, inferSchema=True)
    return df

def load_to_postgres(df, table_name, db_url, user, password):
# Save DataFrame to PostgreSQL database
    df.write.format("jdbc") \
        .option("url", db_url) \
        .option("dbtable", table_name) \
        .option("user", user) \
        .option("password", password) \
        .option("driver", "org.postgresql.Driver") \
        .option("url", "jdbc:postgresql://10.11.1.81:5432/etldb") \
        .mode("overwrite") \
        .save()

def load_data_main(output_transformed, db_url, user, password):
    # Initialize Spark session with master URL(for standalone mode) and adjust memory settings
    spark = SparkSession.builder \
        .appName("LoadDataApp") \
        .master("spark://10.11.1.81:7077") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.jars", "file:/home/pkn/postgresql-42.7.2.jar") \
        .getOrCreate()

    try:
        # Read transformed data into a DataFrame
        transformed_data_df = read_transformed_data(spark, output_transformed)

        # Save tables to PostgreSQL database
        load_to_postgres(transformed_data_df.select("InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "CustomerID"), 'orders_table', db_url, user, password) #fact table
        load_to_postgres(transformed_data_df.select("StockCode", "Description", "UnitPrice").distinct(), 'stock_table', db_url, user, password) #dimension table
        load_to_postgres(transformed_data_df.select("CustomerID", "Country").distinct(), 'customers_table', db_url, user, password) #dimension table

    finally:
        # Stop the Spark session
        spark.stop()

