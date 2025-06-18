from bson import ObjectId
from database import db
from models import TVShow

tvlist_collection = db["tvlist_v3"]
EO_TVLIST = ObjectId("6852164c3da8e93b0fdc67b8")


def add_tv_show(tv_show: TVShow):
    tv_show_data = tv_show.model_dump()
    result = tvlist_collection.update_one(
        {"_id": EO_TVLIST},
        {"$push": {"data": tv_show_data}},
    )
    print(
        f"[added tv show] tv_show_data: {tv_show_data}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


def delete_tv_show(imdb: str):
    result = tvlist_collection.update_one(
        {"_id": EO_TVLIST},
        {"$pull": {"data": {"imdb": imdb}}},
    )
    print(
        f"[deleted show] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


def update_status(imdb: str, new_status: str):
    result = tvlist_collection.update_one(
        {"_id": EO_TVLIST, "data.imdb": imdb},
        {"$set": {"data.$.status": new_status}},
    )
    print(
        f"[updated status] imdb: {imdb}, new_status: {new_status}, matched: {result.matched_count}, modified: {result.modified_count}"
    )


def decrement_progress(imdb: str):
    # Fetch current progress first to avoid negative values
    doc = tvlist_collection.find_one(
        {"_id": EO_TVLIST, "data.imdb": imdb}, {"data.$": 1}
    )
    if not doc or "data" not in doc or len(doc["data"]) == 0:
        print(f"[decremented progress] imdb: {imdb} not found")
        return

    current = doc["data"][0]["currentEpisode"]
    if current > 0:
        result = tvlist_collection.update_one(
            {"_id": EO_TVLIST, "data.imdb": imdb},
            {"$inc": {"data.$.currentEpisode": -1}},
        )
        print(
            f"[decremented progress] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
        )
    else:
        print(f"[decremented progress] imdb: {imdb} already at 0")


def increment_progress(imdb: str):
    # Fetch current progress and totalEpisodes first to avoid exceeding totalEpisodes
    doc = tvlist_collection.find_one(
        {"_id": EO_TVLIST, "data.imdb": imdb}, {"data.$": 1}
    )
    if not doc or "data" not in doc or len(doc["data"]) == 0:
        print(f"[incremented progress] imdb: {imdb} not found")
        return

    show = doc["data"][0]
    if show["currentEpisode"] < show["totalEpisodes"]:
        result = tvlist_collection.update_one(
            {"_id": EO_TVLIST, "data.imdb": imdb},
            {"$inc": {"data.$.currentEpisode": 1}},
        )
        print(
            f"[incremented progress] imdb: {imdb}, matched: {result.matched_count}, modified: {result.modified_count}"
        )
    else:
        print(f"[incremented progress] imdb: {imdb} already at totalEpisodes")
