import bcrypt
from bson import ObjectId
from database import db
from models import User
from user_dal.helpers import create_empty_list_doc
from fastapi import APIRouter, HTTPException, status

users_collection = db["users"]
tvlist_collection = db["tvlist"]
movielist_collection = db["movielist"]


def add_user(_u: User):
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(_u.password.encode(), bcrypt.gensalt()).decode()

    # Create empty tvlist and movielist docs first
    tvlist_id = create_empty_list_doc(tvlist_collection)
    movielist_id = create_empty_list_doc(movielist_collection)

    user_doc = {
        "username": _u.username,
        "password": hashed_password,
        "tvlist": tvlist_id,
        "movielist": movielist_id,
    }

    result = users_collection.insert_one(user_doc)
    print(f"[added user] username: {_u.username}, inserted_id: {result.inserted_id}")


def delete_user(data: User):
    user = users_collection.find_one({"username": data.username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not bcrypt.checkpw(data.password.encode(), user["password"].encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Optionally delete linked tvlist and movielist docs too
    tvlist_id = user.get("tvlist")
    movielist_id = user.get("movielist")

    if tvlist_id:
        tvlist_collection.delete_one({"_id": ObjectId(tvlist_id)})
    if movielist_id:
        movielist_collection.delete_one({"_id": ObjectId(movielist_id)})

    result = users_collection.delete_one({"username": data.username})

    print(
        f"[deleted user] username: {data.username}, deleted_count: {result.deleted_count}"
    )

    return {
        "message": "User and associated data deleted successfully",
        "deleted_count": result.deleted_count,
    }


def change_password(username: str, new_password: str):
    result = users_collection.update_one(
        {"username": username}, {"$set": {"password": new_password}}
    )
    print(
        f"[changed password] username: {username}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


def get_user_tvlist(username: str):
    user = users_collection.find_one({"username": username})
    if not user:
        print(f"[get_user_tvlist] username {username} not found")
        return None

    tvlist_id = user.get("tvlist")
    if not tvlist_id:
        print(f"[get_user_tvlist] No tvlist linked for user {username}")
        return None

    tvlist_doc = tvlist_collection.find_one({"_id": ObjectId(tvlist_id)})
    return tvlist_doc


def get_user_movielist(username: str):
    user = users_collection.find_one({"username": username})
    if not user:
        print(f"[get_user_movielist] username {username} not found")
        return None

    movielist_id = user.get("movielist")
    if not movielist_id:
        print(f"[get_user_movielist] No movielist linked for user {username}")
        return None

    movielist_doc = movielist_collection.find_one({"_id": ObjectId(movielist_id)})
    return movielist_doc
