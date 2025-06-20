from bson import ObjectId
from fastapi import Request
from database import db
from helpers import Helpers
from models import TVShow

tvlist_collection = db["tvlist"]

# ===============================================
# ============== GET TV LIST ====================
# ===============================================


def get_user_tv_list(request: Request):
    user_id = Helpers.get_current_user_id_from_session(request)
    doc = tvlist_collection.find_one({"user": ObjectId(user_id)})
    return doc.get("data", []) if doc else []


# ===============================================
# ============== ADD / REMOVE SHOWS =============
# ===============================================


def add_tv_show(request: Request, tv_show: TVShow):
    user_id = Helpers.get_current_user_id_from_session(request)
    _t = tv_show.model_dump()
    result = tvlist_collection.update_one(
        {"user": ObjectId(user_id)}, {"$push": {"data": _t}}, upsert=True
    )
    print(
        f"[added tv show] user_id: {user_id}, title: {tv_show.title}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


def delete_tv_show(request: Request, imdb: str):
    user_id = Helpers.get_current_user_id_from_session(request)
    result = tvlist_collection.update_one(
        {"user": ObjectId(user_id)},
        {"$pull": {"data": {"imdb": imdb}}},
    )
    print(
        f"[deleted show] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


# ===============================================
# =============== UPDATE STATUS =================
# ===============================================


def update_status(request: Request, imdb: str, new_status: str):
    user_id = Helpers.get_current_user_id_from_session(request)
    result = tvlist_collection.update_one(
        {"user": ObjectId(user_id), "data.imdb": imdb},
        {"$set": {"data.$.status": new_status}},
    )
    print(
        f"[updated status] imdb: {imdb}, new_status: {new_status}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


# ===============================================
# ======== INCREMENT / DECREMENT PROGRESS =======
# ===============================================


def decrement_progress(request: Request, imdb: str):
    user_id = Helpers.get_current_user_id_from_session(request)
    # Fetch current progress first to avoid negative values
    doc = tvlist_collection.find_one(
        {"user": ObjectId(user_id), "data.imdb": imdb}, {"data.$": 1}
    )
    if not doc or "data" not in doc or len(doc["data"]) == 0:
        print(f"[decremented progress] imdb: {imdb} not found")
        return

    current = doc["data"][0]["currentEpisode"]
    if current > 0:
        result = tvlist_collection.update_one(
            {"user": ObjectId(user_id), "data.imdb": imdb},
            {"$inc": {"data.$.currentEpisode": -1}},
        )
        print(
            f"[decremented progress] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
        )
    else:
        print(f"[decremented progress] imdb: {imdb} already at 0")


def increment_progress(request: Request, imdb: str):
    user_id = Helpers.get_current_user_id_from_session(request)
    # Fetch current progress and totalEpisodes first to avoid exceeding totalEpisodes
    doc = tvlist_collection.find_one(
        {"user": ObjectId(user_id), "data.imdb": imdb}, {"data.$": 1}
    )
    if not doc or "data" not in doc or len(doc["data"]) == 0:
        print(f"[incremented progress] imdb: {imdb} not found")
        return

    show = doc["data"][0]
    if show["currentEpisode"] < show["totalEpisodes"]:
        result = tvlist_collection.update_one(
            {"user": ObjectId(user_id), "data.imdb": imdb},
            {"$inc": {"data.$.currentEpisode": 1}},
        )
        print(
            f"[incremented progress] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
        )
    else:
        print(f"[incremented progress] imdb: {imdb} already at totalEpisodes")
