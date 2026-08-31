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

    print(f"LOGIN ATTEMPT: {email}")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    user = UserHelper.get_by_email(email)
    if not user:
        print(f"LOGIN FAILED: User {email} not found")
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    if not UserHelper.verify_password(user['password'], password):
        print(f"LOGIN FAILED: Incorrect password for {email}")
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    print(f"LOGIN SUCCESS: Password verified for {email}. Sending OTP...")

    # Trigger 2FA
    success, error = send_otp_email(user)

    # We now always succeed the request to move to the OTP screen,
    # even if mail failed (we log the code in Rescue Mode)
    return jsonify({
        "success": True,
        "message": "OTP processed",
        "two_factor_required": True,
        "email": email,
        "status": "sent" if not error else "rescue_mode"
    }), 200

@auth_bp.route("/test-email")
def test_email():
    test_user = {"email": "noreplymovemate@gmail.com", "full_name": "MoveMate Admin"}
    success, error = send_otp_email(test_user)
    return jsonify({
        "success": success,
        "message": "Check Render logs for 'MAIL DELIVERED' status",
        "error_if_any": error
    })

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
