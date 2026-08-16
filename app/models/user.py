from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime

class UserHelper:
    """
    Utility class for User operations in MongoDB
    """
    @staticmethod
    def create_user(data):
        hashed_password = generate_password_hash(data['password'])
        user_doc = {
            "full_name": data['full_name'],
            "email": data['email'],
            "phone": data['phone'],
            "password": hashed_password,
            "role": data.get('role', 'customer'),
            "otp_code": None,
            "otp_expiry": None,
            "created_at": datetime.utcnow()
        }
        result = db.users.insert_one(user_doc)
        user_doc['_id'] = str(result.inserted_id)
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
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)
