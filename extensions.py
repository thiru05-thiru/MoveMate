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
            # Re-attempt lazy initialization if possible
            from flask import current_app
            if current_app:
                init_mongodb(current_app)

        if self._db is None:
            raise RuntimeError("Database connection not ready. Check MONGODB_URI.")
        return getattr(self._db, name)

    def set_db(self, database):
        self._db = database

db = MongoDBProxy()

def init_mongodb(app):
    # Use app config or env fallback
    uri = app.config.get("MONGODB_URI") or os.getenv("MONGODB_URI")

    if not uri:
        print("CRITICAL ERROR: MONGODB_URI is not set in .env or Config!")
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

        # Get DB name from URI (e.g. zoventra-main) or fallback
        # This handles the appName parameter correctly
        database = client.get_default_database()

        db.client = client
        db.set_db(database)

        print(f"✅ MONGODB CONNECTED TO: {database.name}")
    except Exception as e:
        print(f"❌ MONGODB CONNECTION FAILED: {str(e)}")
