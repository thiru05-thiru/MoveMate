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


# ==========================================
# CREATE BOOKING
# POST /api/bookings/
# ==========================================
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
                "booking_id": booking.booking_id,
                "driver_id": booking.driver_id,
                "vehicle_id": booking.vehicle_id,
                "pickup_address": booking.pickup_address,
                "destination_address": booking.destination_address,
                "pickup_lat": booking.pickup_lat,
                "pickup_lng": booking.pickup_lng,
                "destination_lat": booking.destination_lat,
                "destination_lng": booking.destination_lng,
                "vehicle_type": booking.vehicle_type,
                "goods_type": booking.goods_type,
                "estimated_weight": booking.estimated_weight,
                "status": booking.status,
                "created_at": booking.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# GET MY BOOKINGS
# GET /api/bookings/
# ==========================================
@booking_bp.route("/", methods=["GET"])
@jwt_required()
def get_my_bookings():
    try:
        customer_id = get_jwt_identity()

        bookings = get_customer_bookings(customer_id)

        booking_list = []

        for booking in bookings:
            booking_list.append({
                "booking_id": booking.booking_id,
                "driver_id": booking.driver_id,
                "vehicle_id": booking.vehicle_id,
                "pickup_address": booking.pickup_address,
                "destination_address": booking.destination_address,
                "pickup_lat": booking.pickup_lat,
                "pickup_lng": booking.pickup_lng,
                "destination_lat": booking.destination_lat,
                "destination_lng": booking.destination_lng,
                "vehicle_type": booking.vehicle_type,
                "goods_type": booking.goods_type,
                "estimated_weight": booking.estimated_weight,
                "status": booking.status,
                "created_at": booking.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({
            "success": True,
            "count": len(booking_list),
            "bookings": booking_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


    # ==========================================
# GET DRIVER BOOKINGS
# GET /api/bookings/driver
# ==========================================

@booking_bp.route("/driver", methods=["GET"])
@jwt_required()
def get_my_driver_bookings():
    try:
        driver_user_id = int(get_jwt_identity())

        bookings = get_driver_bookings(driver_user_id)

        booking_list = []

        for booking in bookings:
            booking_list.append({
                "booking_id": booking.booking_id,
                "pickup_address": booking.pickup_address,
                "destination_address": booking.destination_address,
                "vehicle_type": booking.vehicle_type,
                "goods_type": booking.goods_type,
                "estimated_weight": booking.estimated_weight,
                "status": booking.status,
                "created_at": booking.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({
            "success": True,
            "count": len(booking_list),
            "bookings": booking_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    
    # ==========================================
# GET BOOKING DETAILS
# GET /api/bookings/<booking_id>
# ==========================================
@booking_bp.route("/<booking_id>", methods=["GET"])
@jwt_required()
def booking_details(booking_id):
    try:
        customer_id = get_jwt_identity()

        booking = get_booking_by_id(customer_id, booking_id)

        if booking is None:
            return jsonify({
                "success": False,
                "message": "Booking not found"
            }), 404

        return jsonify({
            "success": True,
            "booking": {
                "booking_id": booking.booking_id,
                "driver_id": booking.driver_id,
                "vehicle_id": booking.vehicle_id,
                "pickup_address": booking.pickup_address,
                "destination_address": booking.destination_address,
                "pickup_lat": booking.pickup_lat,
                "pickup_lng": booking.pickup_lng,
                "destination_lat": booking.destination_lat,
                "destination_lng": booking.destination_lng,
                "vehicle_type": booking.vehicle_type,
                "goods_type": booking.goods_type,
                "estimated_weight": booking.estimated_weight,
                "status": booking.status,
                "created_at": booking.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    # ==========================================
# GET BOOKING TRACKING
# ==========================================

@booking_bp.route("/<string:booking_id>/tracking", methods=["GET"])
@jwt_required()
def booking_tracking(booking_id):

    tracking = get_tracking_details(booking_id)

    if not tracking:
        return jsonify({
            "success": False,
            "message": "Booking not found."
        }), 404

    return jsonify({
        "success": True,
        "tracking": tracking
    }), 200
    
    # ==========================================
# CANCEL BOOKING
# PUT /api/bookings/<booking_id>/cancel
# ==========================================
@booking_bp.route("/<booking_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_booking_route(booking_id):
    try:
        customer_id = get_jwt_identity()

        booking = cancel_booking(customer_id, booking_id)

        if booking is None:
            return jsonify({
                "success": False,
                "message": "Booking not found"
            }), 404

        if booking == "DELIVERED":
            return jsonify({
                "success": False,
                "message": "Delivered bookings cannot be cancelled"
            }), 400

        return jsonify({
            "success": True,
            "message": "Booking cancelled successfully",
            "status": booking.status
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    # ==========================================
# ACCEPT BOOKING
# PUT /api/bookings/<booking_id>/accept
# ==========================================

@booking_bp.route("/<booking_id>/accept", methods=["PUT"])
@jwt_required()
def accept_booking_route(booking_id):
    try:

        driver_user_id = int(get_jwt_identity())
        print("JWT Identity from Route:", driver_user_id)

        booking, error = accept_booking(
            driver_user_id,
            booking_id
        )

        if error:
            return jsonify({
                "success": False,
                "message": error
            }), 404

        return jsonify({
            "success": True,
            "message": "Booking accepted successfully",
            "booking": {
                "booking_id": booking.booking_id,
                "status": booking.status
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    # ==========================================
# START TRIP
# PUT /api/bookings/<booking_id>/start
# ==========================================

@booking_bp.route("/<booking_id>/start", methods=["PUT"])
@jwt_required()
def start_trip_route(booking_id):
    try:

        driver_user_id = int(get_jwt_identity())

        booking, error = start_trip(
            driver_user_id,
            booking_id
        )

        if error:
            return jsonify({
                "success": False,
                "message": error
            }), 404

        return jsonify({
            "success": True,
            "message": "Trip started successfully",
            "booking": {
                "booking_id": booking.booking_id,
                "status": booking.status
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    # ==========================================
# DELIVER TRIP
# PUT /api/bookings/<booking_id>/deliver
# ==========================================

@booking_bp.route("/<booking_id>/deliver", methods=["PUT"])
@jwt_required()
def deliver_trip_route(booking_id):
    try:

        driver_user_id = int(get_jwt_identity())

        booking, error = deliver_trip(
            driver_user_id,
            booking_id
        )

        if error:
            return jsonify({
                "success": False,
                "message": error
            }), 404

        return jsonify({
            "success": True,
            "message": "Trip delivered successfully",
            "booking": {
                "booking_id": booking.booking_id,
                "status": booking.status
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500