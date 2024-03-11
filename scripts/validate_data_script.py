from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, TimestampType, StringType, DoubleType
from pyspark.sql.functions import col

def read_transformed_data(spark, output_transformed):
    # Define the schema based on your expected column names and data types
    expected_schema = StructType([
        StructField('InvoiceNo', StringType(), True),
        StructField('StockCode', StringType(), True), 
        StructField('Description', StringType(), True), 
        StructField('Quantity', IntegerType(), True),
        StructField('InvoiceDate', TimestampType(), True),
        StructField('UnitPrice', DoubleType(), True), 
        StructField('CustomerID', IntegerType(), True), 
        StructField('Country', StringType(), True)
        # Add more fields as needed
    ])

    # Read raw data into a DataFrame without header
    df = spark.read.csv(output_transformed, header=False, schema=expected_schema)

    # Manually assign column names
    df = df.toDF(*[field.name for field in expected_schema.fields])

    df.printSchema()
    df.show(5, truncate=False)
    return df


def check_null_values(df, columns):
    for column in columns:
        null_count = df.filter(col(column).isNull()).count()
        if null_count > 0:
            raise ValueError(f"Null value validation failed. Found {null_count} null values in column: {column}")

def validate_null_values(df): 
    # Use the check_null_values function to check specific columns
    check_null_values(df, ['InvoiceNo', 'StockCode', 'Quantity', 'InvoiceDate', 'CustomerID'])


def validate_duplicates(df):

    # Sort the DataFrame by InvoiceNo before checking for duplicates
    df = df.orderBy("InvoiceNo")
    
    columns_to_check = ['InvoiceNo', 'Stockcode', 'Quantity', 'InvoiceDate', 'CustomerID']

    # Show more information about the duplicates
    duplicate_count = df.groupBy(columns_to_check).count().filter("count > 1").count()

    print(f"Total count of duplicate rows: {duplicate_count}")

     # Show the first few rows with duplicates
    duplicate_rows = df.groupBy(columns_to_check).count().filter("count > 1").show(truncate=False)

    print(f"Here the first duplicate rows: {duplicate_rows}")

    if duplicate_count > 0:
        raise ValueError(f"Duplicate checking failed. Found {duplicate_count} duplicate rows.")

def validate_schema(df):
    expected_schema = StructType([
        StructField('InvoiceNo', StringType(), True),
        StructField('StockCode', StringType(), True), 
        StructField('Description', StringType(), True), 
        StructField('Quantity', IntegerType(), True),
        StructField('InvoiceDate', TimestampType(), True),
        StructField('UnitPrice', DoubleType(), True), 
        StructField('CustomerID', IntegerType(), True), 
        StructField('Country', StringType(), True)
        # Add more fields as needed
    ])

    actual_schema = df.schema

    if actual_schema != expected_schema:
        print("Expected Schema:")
        print(expected_schema)
        print("Actual Schema:")
        print(actual_schema)
        raise ValueError("Schema validation failed. Actual schema doesn't match expected schema.")

def validate_data_main(output_transformed):
    # Initialize Spark session with master URL(for standalone mode) and adjust memory settings
    spark = SparkSession.builder \
        .appName("ValidateDataApp") \
        .master("spark://10.11.1.81:7077") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .getOrCreate()
    

    # Read transformed data into a DataFrame
    transformed_data_df = read_transformed_data(spark, output_transformed)

    # Print DataFrame columns for troubleshooting
    print("DataFrame columns:")
    for col_name in transformed_data_df.columns:
        print(col_name)
    
    # Validate data
    validate_null_values(transformed_data_df)
    validate_duplicates(transformed_data_df)
    validate_schema(transformed_data_df)

    # Stop the Spark session
    spark.stop()
