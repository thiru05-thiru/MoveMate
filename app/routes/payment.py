from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.payment_service import create_razorpay_order, verify_payment

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/create-order", methods=["POST"])
@jwt_required()
def create_order():
    data = request.get_json()
    booking_id = data.get("booking_id")
    amount = data.get("amount")

    if not booking_id or not amount:
        return jsonify({"success": False, "message": "Booking ID and amount are required"}), 400

    order, error = create_razorpay_order(booking_id, amount)

    if error:
        return jsonify({"success": False, "message": error}), 500

    return jsonify({"success": True, "order": order}), 200

@payment_bp.route("/verify", methods=["POST"])
@jwt_required()
def verify():
    data = request.get_json()
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")

    if not all([order_id, payment_id, signature]):
        return jsonify({"success": False, "message": "Missing payment parameters"}), 400

    success, message = verify_payment(order_id, payment_id, signature)

    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message}), 200
