from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)

db = client["beantrack"]

users_collection = db["users"]
tvlist_collection = db["tvlist"]
movielist_collection = db["movielist"]