from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient
import os

# Initialize Extensions
mail = Mail()
cors = CORS(resources={r"/api/*": {"origins": "*"}})

# MongoDB Setup
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
        # Get database name from URI or use default
        db_name = "movemate_db"
        db = mongo_client[db_name]
        print(f"Connected to MongoDB Atlas: {db_name} ✅")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e} ❌")

# We keep this for backward compatibility if any imports still look for it,
# but we will move logic away from it.
class LegacyDB:
    def init_app(self, app):
        pass

db_sqla = LegacyDB()
