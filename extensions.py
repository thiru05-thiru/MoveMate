from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient
import os

# Initialize Extensions
jwt = JWTManager()
mail = Mail()
cors = CORS(resources={r"/api/*": {"origins": "*"}})

# MongoDB Global State
mongo_client = None
db = None

def init_mongodb(app):
    global mongo_client, db
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("CRITICAL: MONGODB_URI not found in environment!")
        return

    try:
        mongo_client = MongoClient(uri)
        # Using the default database provided in Atlas or fallback
        db = mongo_client.get_default_database("movemate_db")
        print(f"Connected to MongoDB Atlas ✅")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e} ❌")
