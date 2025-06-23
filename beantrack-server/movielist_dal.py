from bson import ObjectId
from fastapi import Request
from database import db
from helpers import Helpers
from models import Movie

users_collection = db["users"]
movielist_collection = db["movielist"]

# ===============================================
# ============== GET MOVIE LIST =================
# ===============================================


def get_user_movie_list(request: Request):
    user_id = Helpers.get_current_user_id_from_session(request)
    print(f"User ID from session: {user_id}")

    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    print(f"User doc: {user_doc}")

    if not user_doc or "movielist" not in user_doc:
        print("No movielist found for user")
        return []

    movielist_id = user_doc["movielist"]
    print(f"movielist ObjectId: {movielist_id}")

    movielist_doc = movielist_collection.find_one({"_id": movielist_id})
    print(f"movielist doc: {movielist_doc}")

    if not movielist_doc:
        print("No movielist document found")
        return []

    data = movielist_doc.get("data", [])
    print(f"Data returned: {data}")
    return data


def get_user_movie_list_by_status(request: Request, status: str):
    user_id = Helpers.get_current_user_id_from_session(request)
    print(f"User ID from session: {user_id}")

    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    print(f"User doc: {user_doc}")

    if not user_doc or "movielist" not in user_doc:
        print("No movielist found for user")
        return []

    movielist_id = user_doc["movielist"]
    print(f"movielist ObjectId: {movielist_id}")

    try:
        pipeline = [
            {"$match": {"_id": ObjectId(movielist_id)}},
            {
                "$project": {
                    "data": {
                        "$filter": {
                            "input": "$data",
                            "as": "item",
                            "cond": {"$eq": ["$$item.status", status]},
                        }
                    }
                }
            },
        ]
        movielist_doc = next(movielist_collection.aggregate(pipeline), None)
    except Exception as e:
        print(f"Aggregation error: {e}")
        return []

    if not movielist_doc:
        print("No movielist document found")
        return []

    print(f"Filtered data: {movielist_doc.get('data', [])}")
    return movielist_doc.get("data", [])


# ===============================================
# ============== ADD / REMOVE MOVIES ============
# ===============================================


def add_movie(request: Request, movie: Movie):
    user_id = Helpers.get_current_user_id_from_session(request)
    movielist_id = Helpers.get_current_movielist_id(user_id)

    _m = movie.model_dump()

    result = movielist_collection.update_one(
        {"_id": movielist_id}, {"$push": {"data": _m}}
    )

    print(
        f"[added movie] user_id: {user_id}, title: {movie.title}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


def delete_movie(request: Request, imdb: str):
    user_id = Helpers.get_current_user_id_from_session(request)
    movielist_id = Helpers.get_current_movielist_id(user_id)

    result = movielist_collection.update_one(
        {"_id": movielist_id},
        {"$pull": {"data": {"imdb": imdb}}},
    )

    print(
        f"[deleted movie] user_id: {user_id}, imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


# ===============================================
# ============ UPDATE MOVIE STATUS ==============
# ===============================================


def update_movie_status(request: Request, imdb: str, new_status: str):
    user_id = Helpers.get_current_user_id_from_session(request)
    movielist_id = Helpers.get_current_movielist_id(user_id)

    result = movielist_collection.update_one(
        {"_id": movielist_id, "data.imdb": imdb},
        {"$set": {"data.$.status": new_status}},
    )

    print(
        f"[updated status] user_id: {user_id}, imdb: {imdb}, new_status: {new_status}, matched: {result.matched_count}, modified: {result.modified_count}"
    )
