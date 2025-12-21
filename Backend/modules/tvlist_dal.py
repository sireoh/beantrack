"""
TV list data access layer.
"""

from bson import ObjectId
from fastapi import Request
from .database import db
from .helpers import Helpers
from .models import TVShow

users_collection = db["users"]
tvlist_collection = db["tvlist"]

# ===============================================
# ============== GET TV LIST ====================
# ===============================================


def get_user_tv_list(user_id: str):
    """
    Get the user's TV list.

    :param user_id: The user ID.
    :return: Sorted list of TV shows.
    """
    print(f"User ID from JWT: {user_id}")

    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    # print(f"User doc: {user_doc}")

    if not user_doc or "tvlist" not in user_doc:
        print("No tvlist found for user")
        return []

    tvlist_id = user_doc["tvlist"]
    print(f"tvlist ObjectId: {tvlist_id}")

    tvlist_doc = tvlist_collection.find_one({"_id": tvlist_id})
    # print(f"tvlist doc: {tvlist_doc}")

    if not tvlist_doc:
        print("No tvlist document found")
        return []

    data = tvlist_doc.get("data", [])
    sorted_data = sorted(data, key=lambda x: x.get("title", "").lower())
    # print(f"Data returned (sorted): {sorted_data}")
    return sorted_data


def get_user_tv_list_by_status(user_id: str, status: str):
    """
    Get the user's TV list filtered by status.

    :param user_id: The user ID.
    :param status: The status to filter by.
    :return: Filtered and sorted list of TV shows.
    """
    print(f"User ID from JWT: {user_id}")

    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    # print(f"User doc: {user_doc}")

    if not user_doc or "tvlist" not in user_doc:
        print("No tvlist found for user")
        return []

    tvlist_id = user_doc["tvlist"]
    print(f"tvlist ObjectId: {tvlist_id}")

    try:
        pipeline = [
            {"$match": {"_id": ObjectId(tvlist_id)}},
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
        tvlist_doc = next(tvlist_collection.aggregate(pipeline), None)
    except Exception as e:
        print(f"Aggregation error: {e}")
        return []

    if not tvlist_doc:
        print("No tvlist document found")
        return []

    print(f"Filtered data: {tvlist_doc.get('data', [])}")
    data = tvlist_doc.get("data", [])
    sorted_data = sorted(data, key=lambda x: x.get("title", "").lower())
    # print(f"Data returned (sorted): {sorted_data}")
    return sorted_data


# ===============================================
# ============== ADD / REMOVE SHOWS =============
# ===============================================


def add_tv_show(user_id: str, tv_show: TVShow):
    """
    Add a TV show to the user's list.

    :param user_id: The user ID.
    :param tv_show: The TV show data.
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    _t = tv_show.model_dump()

    result = tvlist_collection.update_one({"_id": tvlist_id}, {"$push": {"data": _t}})

    print(
        f"[added tv show] user_id: {user_id}, title: {tv_show.title}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


def delete_tv_show(user_id: str, imdb: str):
    """
    Delete a TV show from the user's list by IMDb ID.

    :param user_id: The user ID.
    :param imdb: The IMDb ID.
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    result = tvlist_collection.update_one(
        {"_id": tvlist_id},
        {"$pull": {"data": {"imdb": imdb}}},
    )

    print(
        f"[deleted show] user_id: {user_id}, imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


# ===============================================
# ============= UPDATE TV SHOW STATUS ===========
# ===============================================


def update_tv_show_status(user_id: str, imdb: str, new_status: str):
    """
    Update the status of a TV show in the user's list.

    :param user_id: The user ID.
    :param imdb: The IMDb ID.
    :param new_status: The new status.
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    result = tvlist_collection.update_one(
        {"_id": tvlist_id, "data.imdb": imdb},
        {"$set": {"data.$.status": new_status}},
    )

    print(
        f"[updated status] user_id: {user_id}, imdb: {imdb}, new_status: {new_status}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


# ===============================================
# =========== INCREMENT / DECREMENT =============
# ============= TV SHOW PROGRESS ================
# ===============================================


def decrement_tv_show_progress(user_id: str, imdb: str):
    """
    Decrement the progress of a TV show by one episode.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the TV show.
    :return: None
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    doc = tvlist_collection.find_one(
        {"_id": tvlist_id, "data.imdb": imdb}, {"data.$": 1}
    )

    if not doc or "data" not in doc or len(doc["data"]) == 0:
        print(f"[decremented progress] imdb: {imdb} not found")
        return

    current = doc["data"][0].get("currentEpisodeIndex", 0)
    if current > 0:
        result = tvlist_collection.update_one(
            {"_id": tvlist_id, "data.imdb": imdb},
            {"$inc": {"data.$.currentEpisodeIndex": -1}},
        )
        print(
            f"[decremented progress] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
        )
    else:
        print(f"[decremented progress] imdb: {imdb} already at 0")


def increment_tv_show_progress(user_id: str, imdb: str):
    """
    Increment the progress of a TV show by one episode.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the TV show.
    :return: None
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    doc = tvlist_collection.find_one(
        {"_id": tvlist_id, "data.imdb": imdb}, {"data.$": 1}
    )

    if not doc or "data" not in doc or len(doc["data"]) == 0:
        print(f"[incremented progress] imdb: {imdb} not found")
        return

    show = doc["data"][0]
    current = show.get("currentEpisodeIndex", 0)
    total = len(show.get("episodes", []))

    if current < total - 1:
        result = tvlist_collection.update_one(
            {"_id": tvlist_id, "data.imdb": imdb},
            {"$inc": {"data.$.currentEpisodeIndex": 1}},
        )
        print(
            f"[incremented progress] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
        )
    else:
        print(f"[incremented progress] imdb: {imdb} already at last episode ({total})")


def update_by_index_tv_show_progress(user_id: str, imdb: str, index: int):
    """
    Update the progress of a TV show to a specific episode index.

    :param user_id: The user ID.
    :param imdb: The IMDB ID of the TV show.
    :param index: The episode index to set.
    :return: None
    """
    tvlist_id = Helpers.get_current_tvlist_id(user_id)

    # Find the show within the user's tvlist
    doc = tvlist_collection.find_one(
        {"_id": tvlist_id, "data.imdb": imdb}, {"data.$": 1}
    )

    # Validate existence
    if not doc or "data" not in doc or len(doc["data"]) == 0:
        print(f"[update by index progress] imdb: {imdb} not found")
        return

    # Directly update to the provided index
    result = tvlist_collection.update_one(
        {"_id": tvlist_id, "data.imdb": imdb},
        {"$set": {"data.$.currentEpisodeIndex": index}},
    )

    print(
        f"[update by index progress] imdb: {imdb}, set to: {index}, matched: {result.matched_count}, modified: {result.modified_count}"
    )
