"""
Authentication data access layer.
"""

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.db.models import DBUser

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def auth(user_id: str):
    """
    Get authentication info for the current user.

    :param user_id: The user ID.
    :return: User info dict.
    :raises HTTPException: If user not found.
    """
    with SessionLocal() as session:
        user = session.query(User).filter(User.userId == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "username": user.username,
            "avatar": user.avatar,
            "admin": user.userType == "admin",  # Assuming userType indicates admin
        }
