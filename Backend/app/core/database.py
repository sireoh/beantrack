"""
Database connection module.
"""

from sqlalchemy import create_engine
from .config import settings

db_uri = settings.database_uri.replace("postgres://", "postgresql://")
engine = create_engine(db_uri)
