from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import UserHelper
from extensions import db
from app.services.email_service import send_otp_email
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/test")
def test():
    return {"message": "Authentication Route Working 🚀"}

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()

    if UserHelper.get_by_email(email):
        return jsonify({"success": False, "message": "Email already registered"}), 400

    if UserHelper.get_by_phone(phone):
        return jsonify({"success": False, "message": "Phone number already registered"}), 400

    UserHelper.create_user(data)
    return jsonify({"success": True, "message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    user = UserHelper.get_by_email(email)
    if not user or not UserHelper.verify_password(user['password'], password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # Trigger 2FA
    success, error = send_otp_email(user)
    if not success:
        print(f"SMTP Error: {error}")
        return jsonify({"success": False, "message": f"Verification error: {error}"}), 500

    return jsonify({
        "success": True,
        "message": "OTP sent",
        "two_factor_required": True,
        "email": email
    }), 200

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    otp = data.get("otp")

    user = UserHelper.get_by_email(email)
    if not user or user.get('otp_code') != otp:
        return jsonify({"success": False, "message": "Invalid code"}), 401

    if user['otp_expiry'] < datetime.utcnow():
        return jsonify({"success": False, "message": "Code expired"}), 401

    # Clear OTP
    db.users.update_one({"email": email}, {"$set": {"otp_code": None, "otp_expiry": None}})

    access_token = create_access_token(
        identity=user['_id'],
        additional_claims={"role": user['role']}
    )

    return jsonify({
        "success": True,
        "token": access_token,
        "user": {
            "id": user['_id'],
            "full_name": user['full_name'],
            "email": user['email'],
            "role": user['role']
        }
    }), 200
