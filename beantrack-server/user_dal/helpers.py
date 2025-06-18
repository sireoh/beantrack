def create_empty_list_doc(collection):
    """Helper to create empty list doc with empty data array and return its ObjectId."""
    res = collection.insert_one({"data": []})
    return res.inserted_id
