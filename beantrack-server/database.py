from pymongo import MongoClient
import os

MONGODB_URI = os.environ["MONGODB_URI"]
client = MongoClient(MONGODB_URI)

db = client["beantrack"]

movielist_collection = db["movielist"]

