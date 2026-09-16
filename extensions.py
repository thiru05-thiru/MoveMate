from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Extensions
jwt = JWTManager()
mail = Mail()
cors = CORS()

# MongoDB Proxy to handle cloud connection state
class MongoDBProxy:
    def __init__(self):
        self._db = None
        self.client = None
        self.name = "N/A"

    def __getattr__(self, name):
        if self._db is None:
            from flask import current_app
            if current_app:
                init_mongodb(current_app)

        if self._db is None:
            raise RuntimeError("Database connection not ready. Check MONGODB_URI.")
        return getattr(self._db, name)

    def set_db(self, database):
        self._db = database
        if database is not None:
            self.name = database.name

db = MongoDBProxy()

def init_mongodb(app):
    uri = app.config.get("MONGODB_URI") or os.getenv("MONGODB_URI")

    if not uri:
        print("CRITICAL ERROR: MONGODB_URI is not set!")
        return

    uri = uri.strip().strip("'").strip('"')

    try:
        print(f"🛰️ ATTEMPTING MONGODB CONNECTION (Cloud Optimized)...")

        # Connection options that work across Local, Render, and Atlas
        # connect=False is crucial for multi-process environments like Render
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=20000,
            tls=True,
            tlsAllowInvalidCertificates=True,
            retryWrites=True,
            connect=False
        )

        # Trigger connection
        client.admin.command('ping')

        # 2. Get Database Name
        # Fallback to zoventra_supreme for the new clean start
        try:
            database = client.get_default_database()
        except:
            database = client.get_database("zoventra_supreme")

        db.client = client
        db.set_db(database)

        print(f"✅ MONGODB CONNECTED TO: {database.name}")
    except Exception as e:
        print(f"❌ MONGODB CONNECTION FAILED: {str(e)}")
        # We don't raise the error here to allow the Flask app to still boot
        # and provide diagnostic info via the root route.
