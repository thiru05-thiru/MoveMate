from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime
from bson import ObjectId
from app.models.driver import DriverHelper

class UserHelper:
    """
    Utility class for User operations in MongoDB
    """
    @staticmethod
    def create_user(data):
        hashed_password = generate_password_hash(data['password'])
        role = data.get('role', 'customer')

        user_doc = {
            "full_name": data['full_name'],
            "email": data['email'],
            "phone": data['phone'],
            "password": hashed_password,
            "role": role,
            "profile_photo": None,
            "location": data.get('location', 'Bangalore, Karnataka'),
            "otp_code": None,
            "otp_expiry": None,
            "created_at": datetime.utcnow()
        }
        result = db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        user_doc['_id'] = user_id

        # If it's a driver, create the driver profile immediately
        if role == 'driver':
            DriverHelper.create_driver(user_id, data)

        return user_doc

    @staticmethod
    def get_by_email(email):
        user = db.users.find_one({"email": email})
        if user:
            user['_id'] = str(user['_id'])
        return user

    @staticmethod
    def get_by_phone(phone):
        user = db.users.find_one({"phone": phone})
        if user:
            user['_id'] = str(user['_id'])
        return user

    @staticmethod
    def get_by_id(user_id):
        try:
            if not ObjectId.is_valid(user_id):
                print(f"INVALID ID: {user_id}")
                return None

            user = db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                user.pop('password', None)
            return user
        except Exception as e:
            print(f"GET_BY_ID ERROR: {str(e)}")
            return None

    @staticmethod
    def update_user(user_id, update_data):
        try:
            if not ObjectId.is_valid(user_id):
                return None

            # Prevent critical fields from being updated directly
            update_data.pop('password', None)
            update_data.pop('email', None)
            update_data.pop('_id', None)

            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {**update_data, "updated_at": datetime.utcnow()}}
            )
            return UserHelper.get_by_id(user_id)
        except Exception as e:
            print(f"UPDATE_USER ERROR: {str(e)}")
            return None

    @staticmethod
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)
