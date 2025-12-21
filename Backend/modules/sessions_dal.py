"""
Authentication data access layer.
"""

from bson import ObjectId
from fastapi import HTTPException, Request, status, Response, Cookie
from .database import db
from .helpers import Helpers
from .models import User
import bcrypt

users_collection = db["users"]

# ===============================================
# ============== AUTH ===========================
# ===============================================


def authenticate_user(data: User) -> str:
    """
    Authenticate a user and return their ID.

    :param data: User login data.
    :return: User ID string.
    :raises HTTPException: If user not found or invalid credentials.
    """
    found_user = users_collection.find_one({"username": data.username})

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not bcrypt.checkpw(data.password.encode(), found_user["password"].encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return str(found_user["_id"])
