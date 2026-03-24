"""
Database initialization script
"""

import os
import sys
sys.path.append('src')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.models.database import Base

def init_database():
    """Initialize the database"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://neuro_user:neuro_pass@localhost:5432/neuro_genomic')
    
    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()