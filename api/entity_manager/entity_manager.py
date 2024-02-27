# coordinator for handling data entities within an application
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Get db credentials from environment variables
db_url = os.environ.get("DATABASE_URL")

# Create a SQLAlchemy engine
engine = create_engine(db_url)

# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# EntityManager class for handling database sessions
class EntityManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_session(self):
        return self.session_factory()

# Instantiate the EntityManager
entity_manager = EntityManager(SessionLocal)