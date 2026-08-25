from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.driver_service import (
    register_driver,
    go_online,
    go_offline,
    get_driver_status,
    update_driver_location,
    get_driver_location,
    get_available_drivers,
    find_nearest_driver,
    get_driver_jobs
)

driver_bp = Blueprint("driver", __name__)


# =====================================
# Driver Registration
# =====================================

@driver_bp.route("/register", methods=["POST"])
@jwt_required()
def register():

    data = request.get_json()

    user_id = get_jwt_identity()

    result, error = register_driver(
        user_id=user_id,
        license_number=data.get("license_number"),
        aadhaar_number=data.get("aadhaar_number"),
        pan_number=data.get("pan_number"),
        vehicle_type=data.get("vehicle_type"),
        vehicle_number=data.get("vehicle_number"),
        brand=data.get("brand"),
        model=data.get("model"),
        max_weight=data.get("max_weight"),
        rc_number=data.get("rc_number")
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    return jsonify({
        "success": True,
        "message": "Driver registered successfully",
        "data": result
    }), 201


# =====================================
# Go Online
# =====================================

@driver_bp.route("/go-online", methods=["PUT"])
@jwt_required()
def driver_go_online():

    user_id = get_jwt_identity()

    result, error = go_online(user_id)

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "message": "Driver is now online",
        "data": result
    }), 200


# =====================================
# Go Offline
# =====================================

@driver_bp.route("/go-offline", methods=["PUT"])
@jwt_required()
def driver_go_offline():

    user_id = get_jwt_identity()

    result, error = go_offline(user_id)

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "message": "Driver is now offline",
        "data": result
    }), 200


# =====================================
# Driver Status
# =====================================

@driver_bp.route("/status", methods=["GET"])
@jwt_required()
def driver_status():

    user_id = get_jwt_identity()

    result, error = get_driver_status(user_id)

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "data": result
    }), 200

# =====================================
# Update Driver Location
# =====================================

@driver_bp.route("/location", methods=["PUT"])
@jwt_required()
def update_location():

    data = request.get_json()

    user_id = get_jwt_identity()

    result, error = update_driver_location(
        user_id=user_id,
        latitude=data.get("latitude"),
        longitude=data.get("longitude")
    )

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "message": "Driver location updated successfully",
        "data": result
    }), 200


# =====================================
# Get Driver Location
# =====================================

@driver_bp.route("/location", methods=["GET"])
@jwt_required()
def get_location():

    user_id = get_jwt_identity()

    result, error = get_driver_location(user_id)

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "data": result
    }), 200

# =====================================
# Get Available Drivers (Testing)
# =====================================

# =====================================
# Find Nearest Driver (Testing)
# =====================================

@driver_bp.route("/nearest", methods=["POST"])
@jwt_required()
def nearest_driver():

    data = request.get_json()

    nearest = find_nearest_driver(
        pickup_latitude=data.get("latitude"),
        pickup_longitude=data.get("longitude")
    )

    if not nearest:
        return jsonify({
            "success": False,
            "message": "No available drivers found."
        }), 404

    return jsonify({
        "success": True,
        "data": nearest
    }), 200

# =====================================
# Driver Jobs
# =====================================

@driver_bp.route("/jobs", methods=["GET"])
@jwt_required()
def driver_jobs():

    user_id = get_jwt_identity()

    jobs, error = get_driver_jobs(user_id)

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 404

    return jsonify({
        "success": True,
        "count": len(jobs),
        "jobs": jobs
    }), 200