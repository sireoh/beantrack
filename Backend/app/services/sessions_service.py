"""
Authentication data access layer.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.db.models import DBUser
import bcrypt

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===============================================
# ============== AUTH ===========================
# ===============================================


def authenticate_user(data) -> str:
    """
    Authenticate a user and return their ID.

    :param data: User login data.
    :return: User ID string.
    :raises HTTPException: If user not found or invalid credentials.
    """
    with SessionLocal() as session:
        found_user = (
            session.query(DBUser).filter(DBUser.username == data.username).first()
        )

        if not found_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not bcrypt.checkpw(data.password.encode(), found_user.password.encode()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        return str(found_user.user_id)
