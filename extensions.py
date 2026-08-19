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
        # Use simple initialization for better compatibility with cloud providers
        mongo_client = MongoClient(uri, serverSelectionTimeoutMS=10000)

        # Ping the server to verify connection
        mongo_client.admin.command('ping')

        # Attempt to get database from URI, or fallback to default
        try:
            db = mongo_client.get_default_database()
        except:
            db = mongo_client["movemate_db"]

        print(f"CONNECTED TO MONGODB ATLAS ✅ (DB: {db.name})")
    except Exception as e:
        print(f"DATABASE CONNECTION FAILED: {str(e)} ❌")
