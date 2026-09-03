from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import UserHelper
from extensions import db
from app.services.otp_service import OTPService
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    # 1. User Validation
    user = UserHelper.get_by_email(email)
    if not user or not UserHelper.verify_password(user['password'], password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # 2. Create OTP (DB)
    otp_code = OTPService.create_otp(email)
    if not otp_code:
        return jsonify({"success": False, "message": "Internal error generating security code"}), 500

    # 3. Send OTP (Email)
    # Note: We do this synchronously to ensure the user is notified if the mail server is down
    success, error = OTPService.send_email(email, otp_code, user.get('full_name', 'User'))

    if not success:
        # Emergency backup: If email fails, we log it so admin can assist
        print(f"🚨 ALERT: Email delivery failed for {email}. Code: {otp_code}")
        # In a real public app, you might want to return 500 here,
        # but we'll return 200 with a flag for now so the app doesn't 'Network Error'
        return jsonify({
            "success": True,
            "two_factor_required": True,
            "email": email,
            "warning": "Email service is slow. Please check logs if code doesn't arrive."
        }), 200

    return jsonify({
        "success": True,
        "message": "Verification code sent to your email",
        "two_factor_required": True,
        "email": email
    }), 200

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    otp = data.get("otp")

    # Use the new centralized verification logic
    success, message = OTPService.verify_otp(email, otp)

    if not success:
        return jsonify({"success": False, "message": message}), 401

    # Get user again to create token
    user = UserHelper.get_by_email(email)
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

@auth_bp.route("/test")
def test():
    return {"message": "Authentication System Online 🚀"}
