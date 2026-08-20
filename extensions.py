from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient
import os

# Initialize Extensions
jwt = JWTManager()
mail = Mail()
cors = CORS(resources={r"/api/*": {"origins": "*"}})

# MongoDB Proxy to handle rebinding during app initialization
class MongoDBProxy:
    def __init__(self):
        self._db = None
        self.client = None

    def __getattr__(self, name):
        if self._db is None:
            # Fallback for early access if needed, though init_mongodb should run first
            raise RuntimeError("Database not initialized. Call init_mongodb first.")
        return getattr(self._db, name)

    def set_db(self, database):
        self._db = database

# Global database object used across the app
db = MongoDBProxy()

def init_mongodb(app):
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("CRITICAL ERROR: MONGODB_URI not found!")
        return

    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=10000,
            tlsAllowInvalidCertificates=True
        )
        # Verify connection
        client.admin.command('ping')

        # Set the global proxy database
        try:
            database = client.get_default_database()
        except:
            database = client["movemate_db"]

        db.client = client
        db.set_db(database)

        print(f"CONNECTED TO MONGODB ATLAS ✅ (DB: {database.name})")
    except Exception as e:
        print(f"DATABASE CONNECTION FAILED: {str(e)} ❌")
