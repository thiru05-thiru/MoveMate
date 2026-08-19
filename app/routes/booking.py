from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.booking_service import (
    create_booking,
    get_customer_bookings,
    get_driver_bookings,
    get_booking_by_id,
    get_tracking_details,
    cancel_booking,
    accept_booking,
    start_trip,
    deliver_trip
)

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/", methods=["POST"])
@jwt_required()
def create_new_booking():
    try:
        data = request.get_json()
        customer_id = get_jwt_identity()
        booking = create_booking(customer_id, data)

        return jsonify({
            "success": True,
            "message": "Booking created successfully",
            "booking": {
                "booking_id": booking['booking_id'],
                "status": booking['status']
            }
        }), 201
    except Exception as e:
        print(f"Booking Error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@booking_bp.route("/", methods=["GET"])
@jwt_required()
def get_my_bookings():
    try:
        customer_id = get_jwt_identity()
        bookings = get_customer_bookings(customer_id)
        return jsonify({"success": True, "count": len(bookings), "bookings": bookings}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@booking_bp.route("/driver", methods=["GET"])
@jwt_required()
def get_my_driver_bookings():
    try:
        driver_user_id = get_jwt_identity()
        bookings = get_driver_bookings(driver_user_id)
        return jsonify({"success": True, "count": len(bookings), "bookings": bookings}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@booking_bp.route("/<booking_id>", methods=["GET"])
@jwt_required()
def booking_details(booking_id):
    try:
        customer_id = get_jwt_identity()
        booking = get_booking_by_id(customer_id, booking_id)
        if not booking:
            return jsonify({"success": False, "message": "Booking not found"}), 404
        return jsonify({"success": True, "booking": booking}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@booking_bp.route("/<string:booking_id>/tracking", methods=["GET"])
@jwt_required()
def booking_tracking(booking_id):
    tracking = get_tracking_details(booking_id)
    if not tracking:
        return jsonify({"success": False, "message": "Booking not found."}), 404
    return jsonify({"success": True, "tracking": tracking}), 200

@booking_bp.route("/<booking_id>/accept", methods=["PUT"])
@jwt_required()
def accept_booking_route(booking_id):
    try:
        driver_user_id = get_jwt_identity()
        booking, error = accept_booking(driver_user_id, booking_id)
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "message": "Accepted", "booking": booking}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@booking_bp.route("/<booking_id>/start", methods=["PUT"])
@jwt_required()
def start_trip_route(booking_id):
    try:
        driver_user_id = get_jwt_identity()
        booking, error = start_trip(driver_user_id, booking_id)
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "message": "Started", "booking": booking}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@booking_bp.route("/<booking_id>/deliver", methods=["PUT"])
@jwt_required()
def deliver_trip_route(booking_id):
    try:
        driver_user_id = get_jwt_identity()
        booking, error = deliver_trip(driver_user_id, booking_id)
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "message": "Delivered", "booking": booking}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
