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
        if database:
            self.name = database.name

db = MongoDBProxy()

def init_mongodb(app):
    uri = app.config.get("MONGODB_URI") or os.getenv("MONGODB_URI")

    if not uri:
        print("CRITICAL ERROR: MONGODB_URI is not set!")
        return

    uri = uri.strip().strip("'").strip('"')

    try:
        print(f"🛰️ ATTEMPTING MONGODB CONNECTION...")

        # Use certifi for secure SSL connection on cloud platforms like Render
        import certifi
        ca = certifi.where()

        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=20000,
            tlsCAFile=ca,
            tls=True,
            retryWrites=True
        )

        # 1. Verify connection
        client.admin.command('ping')

        # 2. Get Database Name
        # Fallback to zoventra_supreme for the new clean start
        try:
            database = client.get_default_database()
        except:
            # Manually fallback if the URI doesn't have a /db-name
            database = client.get_database("zoventra_supreme")

        db.client = client
        db.set_db(database)

        print(f"✅ MONGODB CONNECTED TO: {database.name}")
    except Exception as e:
        print(f"❌ MONGODB CONNECTION FAILED: {str(e)}")
        # We don't raise the error here to allow the Flask app to still boot
        # and provide diagnostic info via the root route.
