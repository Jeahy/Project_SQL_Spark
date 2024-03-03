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

# SQL commands to create the database and tables
CREATE_DATABASE_QUERY = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))

CREATE_USERS_TABLE_QUERY = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL
    );
"""

CREATE_ACTIVE_SESSIONS_TABLE_QUERY = """
    CREATE TABLE active_sessions (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) REFERENCES users(username),
        access_token VARCHAR(255) NOT NULL,
        expiry_time TIMESTAMPTZ NOT NULL
    );
"""

# Connect to the default PostgreSQL database (usually "postgres") to create the new database
create_db_conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
create_db_conn.autocommit = True  # Enable autocommit to execute DDL statements
create_db_cursor = create_db_conn.cursor()

# Create the new database
create_db_cursor.execute(CREATE_DATABASE_QUERY)

# Close the cursor and connection
create_db_cursor.close()
create_db_conn.close()

# Connect to the newly created database
with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT) as conn:
    with conn.cursor() as cursor:
        # Create the "users" table
        cursor.execute(CREATE_USERS_TABLE_QUERY)

        # Create the "active_sessions" table
        cursor.execute(CREATE_ACTIVE_SESSIONS_TABLE_QUERY)

print("Database and tables created successfully.")
