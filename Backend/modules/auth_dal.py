"""
Authentication data access layer.
"""

from bson import ObjectId
from fastapi import HTTPException, Request
from .helpers import Helpers
from .database import db

users_collection = db["users"]


def auth(user_id: str):
    """
    Get authentication info for the current user.

    :param user_id: The user ID.
    :return: User info dict.
    :raises HTTPException: If user not found.
    """
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "username": user["username"],
        "avatar": user.get("avatar", None),
        "admin": user["admin"],
    }
