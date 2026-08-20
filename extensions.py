from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient
import os

# Initialize Extensions
jwt = JWTManager()
mail = Mail()
# We define CORS but we'll apply it fully in __init__.py
cors = CORS()

# MongoDB Proxy to handle cloud connection state
class MongoDBProxy:
    def __init__(self):
        self._db = None
        self.client = None

    def __getattr__(self, name):
        if self._db is None:
            raise RuntimeError("Database connection not ready. Check MONGODB_URI.")
        return getattr(self._db, name)

    def set_db(self, database):
        self._db = database

db = MongoDBProxy()

def init_mongodb(app):
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("CRITICAL: MONGODB_URI missing!")
        return

    try:
        # Optimized connection for Render and Atlas
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            tlsAllowInvalidCertificates=True
        )
        # Verify connection immediately
        client.admin.command('ping')

        # Get DB name from URI or fallback
        database = client.get_default_database("movemate_db")

        db.client = client
        db.set_db(database)

        print(f"✅ MONGODB CONNECTED: {database.name}")
    except Exception as e:
        print(f"❌ MONGODB ERROR: {str(e)}")
