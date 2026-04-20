from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✅ Connected to MongoDB")
except ConnectionFailure:
    print("❌ MongoDB connection failed")
    client = None

db                = client["route_optimizer"] if client else None
routes_collection = db["routes"] if db is not None else None    