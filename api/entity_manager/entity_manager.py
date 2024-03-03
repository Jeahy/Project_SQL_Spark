# coordinator for handling data entities within an application
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

db_url = os.environ.get("DATABASE_URL")

class EntityManager:
    def __init__(self, db_url):
        self.db_url = db_url
        print(f"DB URL: {db_url}")  # Print the value of db_url for debugging

    def get_session(self):
        # Create a SQLAlchemy engine
        engine = create_engine(db_url)
        # Create the session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return self.SessionLocal()

# Instantiate the EntityManager
entity_manager = EntityManager(db_url)