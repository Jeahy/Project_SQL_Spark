import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment variables from the .env file
load_dotenv()

# Retrieve environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


CREATE_USERS_TABLE_QUERY = """
    CREATE TABLE users (
        username VARCHAR(50) PRIMARY KEY,
        full_name VARCHAR(50),
        email VARCHAR(50),
        hashed_password VARCHAR(100) NOT NULL,
        disabled BOOLEAN
    );
"""

# SQL command to insert data into the "users" table
INSERT_USERS_DATA_QUERY = """
    INSERT INTO users (username, full_name, email, hashed_password, disabled)
    VALUES 
    ('tim', 'Tim Russo', 'tim@gmail.com', '$2b$12$HxWHkvMuL7WrZad6lcCfluNFj1/Zp63lvP5aUrKlSTYtoFzPXHOtu', False),
    ('anna', 'Anna Moss', 'anna@gmail.com', '$2b$12$iUAQ4TKFRd9DmUAGKvfVb.MNaCX65NWnOY3QiOOqI53ue6rlnUHJq', False);
"""

# Connect to the default PostgreSQL database (usually "postgres") to create the new database
db_conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
db_conn.autocommit = True  # Enable autocommit to execute DDL statements
db_cursor = db_conn.cursor()

# Drop the existing database if it exists
drop_db_query = f"DROP DATABASE IF EXISTS {DB_NAME};"
db_cursor.execute(drop_db_query)

# Create the new database
db_cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))

# Close the cursor and connection
db_cursor.close()
db_conn.close()

# Connect to the newly created database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

# Create the "users" table
with conn.cursor() as cursor:
    cursor.execute(CREATE_USERS_TABLE_QUERY)

# Insert data into the "users" table
with conn.cursor() as cursor:
    cursor.execute(INSERT_USERS_DATA_QUERY)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database, table and data inserted successfully.")