import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

def create_db_main(user, password, host, port, new_db_name, db_url):
    # Replace these with your actual PostgreSQL connection details


    # Connect to the default 'postgres' database
    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
    conn.autocommit = True  # Set autocommit mode

    # Drop the existing database if it exists
    drop_db_query = f"DROP DATABASE IF EXISTS {new_db_name};"
    with conn.cursor() as cursor:
        cursor.execute(drop_db_query)
        print(f"Database '{new_db_name}' dropped successfully (if it existed).")

    # Create a new database
    create_db_query = f"CREATE DATABASE {new_db_name};"

    try:
        with conn.cursor() as cursor:
            cursor.execute(create_db_query)
        print(f"Database '{new_db_name}' created successfully!")

        # Connect to the newly created database
        engine = create_engine(db_url)
        # Perform additional operations on the new database if needed

    except ProgrammingError as e:
        print(f"Error: {e}")
        
