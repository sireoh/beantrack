"""
Authentication data access layer.
"""

from bson import ObjectId
from fastapi import HTTPException, Request
from helpers import Helpers
from database import db

users_collection = db["users"]


def auth(request: Request):
    """
    Get authentication info for the current user.

    :param request: The request object.
    :return: User info dict.
    :raises HTTPException: If user not found.
    """
    user_id = Helpers.get_current_user_id_from_session(request)
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "username": user["username"],
        "avatar": user.get("avatar", None),
        "admin": user["admin"],
    }
