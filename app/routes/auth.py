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

    # 1. Verify User
    user = UserHelper.get_by_email(email)
    if not user or not UserHelper.verify_password(user['password'], password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # 2. Create Security Code
    otp_code = OTPService.create_and_store_otp(email)

    # 3. Send Professional Email
    # We do this during the request to ensure the worker doesn't kill the process
    success, error = OTPService.send_professional_email(email, otp_code)

    return jsonify({
        "success": True,
        "message": "OTP sent to your inbox" if success else "OTP generated (Server busy)",
        "two_factor_required": True,
        "email": email,
        "delivery_status": "inbox" if success else "logs_only"
    }), 200

@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    if not email: return jsonify({"success": False}), 400

    otp_code = OTPService.create_and_store_otp(email)
    success, _ = OTPService.send_professional_email(email, otp_code)

    return jsonify({"success": True, "message": "A new code has been sent."}), 200

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    otp = data.get("otp")

    success, message = OTPService.verify_code(email, otp)
    if not success:
        return jsonify({"success": False, "message": message}), 401

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
    if UserHelper.get_by_email(email):
        return jsonify({"success": False, "message": "Email already exists"}), 400
    UserHelper.create_user(data)
    return jsonify({"success": True, "message": "Registered successfully"}), 201
