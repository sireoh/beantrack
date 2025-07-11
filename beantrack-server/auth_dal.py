from bson import ObjectId
from fastapi import HTTPException, Request
from helpers import Helpers
from database import db

users_collection = db["users"]


def get_auth(request: Request):
    user_id = Helpers.get_current_user_id_from_session(request)
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "username": user["username"],
        "avatar": user.get("avatar", None),
        "admin": user["admin"],
    }
