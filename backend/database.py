from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
from config import Config

# Create base class for models
Base = declarative_base()

# Create engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session - CORRECTED VERSION"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alternative simple version (without generator):
def get_db_session():
    """Simple function to get a database session"""
    return SessionLocal()