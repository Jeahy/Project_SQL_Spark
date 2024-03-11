from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, TimestampType, StringType, DoubleType
from sqlalchemy import create_engine
import pandas as pd

# Add the path to the PostgreSQL JDBC driver JAR file
postgres_jdbc_driver_path = "/opt/spark/jars/postgresql-42.7.2.jar"


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

def load_to_postgres(df, table_name, db_url, jdbc_db_url, user, password):
    # Convert Spark DataFrame to Pandas DataFrame
    pandas_df = df.toPandas()

    # Create SQLAlchemy engine
    engine = create_engine(db_url)

    try:
     # Write DataFrame to PostgreSQL using Spark DataFrame writer
        df.write.format("jdbc").option("url", jdbc_db_url).option("dbtable", table_name).option("user", user).option("password", password).mode("overwrite").save()
    
    except Exception as e:
        print(f"Error: {e}")

def load_data_main(output_transformed, db_url, jdbc_db_url, user, password):
    try:
        spark = SparkSession.builder \
            .appName("ValidateDataApp") \
            .master("spark://10.11.1.81:7077") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .config("spark.jars", f"{postgres_jdbc_driver_path}") \
            .getOrCreate()
        
        # Read transformed data into a DataFrame
        transformed_data_df = read_transformed_data(spark, output_transformed)

        # Print columns for debugging
        print("Columns in transformed_data_df:", transformed_data_df.columns)

        # Save tables to PostgreSQL database
        load_to_postgres(transformed_data_df[["InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "CustomerID"]],
                         'orders_table', db_url, jdbc_db_url, user, password)  # fact table
        load_to_postgres(transformed_data_df[["StockCode", "Description", "UnitPrice"]].drop_duplicates(),
                         'stock_table', db_url, jdbc_db_url, user, password)  # dimension table
        load_to_postgres(transformed_data_df[["CustomerID", "Country"]].drop_duplicates(),
                         'customers_table', db_url, jdbc_db_url, user, password)  # dimension table

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Stop the Spark session
        spark.stop()
