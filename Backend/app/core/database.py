"""
Database connection module.
"""

from sqlalchemy import create_engine
from .config import settings

DATABASE_URI = settings.database_uri.replace("postgres://", "postgresql://")
engine = create_engine(DATABASE_URI)
