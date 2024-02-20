import findspark
findspark.init('/opt/spark')
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp
from pyspark.sql.types import StringType, DoubleType, IntegerType
from pyspark.sql.functions import count, when
from scripts.config import input_raw, output_transformed


def display_data_info(df):
    # Display the schema and sample data
    df.printSchema()
    df.show(5, truncate=False)


def clean_data(df):
    # Display count of null values before cleaning
    print("Null values count before cleaning:")
    df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).show(truncate=False)

    # Drop rows where any of the specified columns have null values
    columns_to_check = ['InvoiceNo', 'StockCode', 'Quantity', 'InvoiceDate', 'CustomerID']
    df = df.dropna(subset=columns_to_check)

    # Display count of null values after cleaning
    print("Null values count after cleaning:")
    df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).show(truncate=False)

    # Removing Duplicate Entries
    df = df.dropDuplicates(['InvoiceNo', 'StockCode', 'Quantity', 'InvoiceDate', 'CustomerID'])

    return df


def transform_data(df):
    # Define the date format pattern
    date_format_pattern = "MM/dd/yyyy HH:mm"

    # Adjust data types for specific columns
    df = df.withColumn("InvoiceDate", to_timestamp(col("InvoiceDate"), date_format_pattern))

    return df


def clean_transform_main(input_path, output_path):
    # Initialize Spark session with master URL(for standalone mode) and adjust memory settings
    spark = SparkSession.builder \
        .appName("CleanTransformApp") \
        .master("spark://Jessicas-MBP:7077") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .getOrCreate()

    # Read raw data into a DataFrame using import_data_script
    raw_data_df = spark.read.csv(input_path, header=True, inferSchema=True)
    
    # Display raw data information
    display_data_info(raw_data_df)

    # Clean the data
    cleaned_df = clean_data(raw_data_df)

    # Transform the data
    transformed_df = transform_data(cleaned_df)

    # Display transformed data information
    display_data_info(transformed_df)

    # Write the result to a new location
    
    transformed_df.write.parquet(output_path, mode="overwrite")

    # Stop the Spark session
    spark.stop()

