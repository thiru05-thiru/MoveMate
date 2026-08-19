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
        print("CRITICAL ERROR: MONGODB_URI not found in environment!")
        return

    try:
        print(f"Connecting to MongoDB with URI: {uri[:20]}...")
        mongo_client = MongoClient(uri)
        # Force a connection check
        mongo_client.admin.command('ping')
        db = mongo_client.get_default_database("movemate_db")
        print(f"Connection Successful! Active DB: {db.name} ✅")
    except Exception as e:
        print(f"DATABASE CONNECTION FAILED: {str(e)} ❌")
