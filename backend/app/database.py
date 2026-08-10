# ============================================================
# NexRay AI - Database Configuration
# This file sets up the database connection using SQLAlchemy.
# We are using SQLite which stores everything in a single file
# called nexray.db inside the backend folder.
# ============================================================

from sqlalchemy import create_engine  # Creates the connection to the database
from sqlalchemy.ext.declarative import declarative_base  # Base class for all our database models
from sqlalchemy.orm import sessionmaker  # Creates database sessions for each request

# The database URL - tells SQLAlchemy to use SQLite and where to store the file
# The file nexray.db will be created automatically in the backend folder
DATABASE_URL = "sqlite:///./nexray.db"

# Create the database engine - this is the core connection to the database
# check_same_thread=False is needed for SQLite to work properly with FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a session factory - each request to the backend gets its own session
# autocommit=False means we manually control when data is saved
# autoflush=False means data isn't sent to the database until we commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our database models will inherit from
# When we create a model like PatientSession, it extends this Base
Base = declarative_base()

# This function gives each route a database session and closes it when done
# We'll use this in every route that needs to talk to the database
def get_db():
    db = SessionLocal()  # Open a new database session
    try:
        yield db  # Give the session to the route that requested it
    finally:
        db.close()  # Always close the session when the request is done