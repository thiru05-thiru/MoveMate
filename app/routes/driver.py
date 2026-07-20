from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.driver_service import register_driver

driver_bp = Blueprint("driver", __name__)


@driver_bp.route("/register", methods=["POST"])
@jwt_required()
def register():

    data = request.get_json()

    user_id = int(get_jwt_identity())

    result, error = register_driver(
        user_id=user_id,
        license_number=data.get("license_number"),
        aadhaar_number=data.get("aadhaar_number"),
        vehicle_type=data.get("vehicle_type"),
        vehicle_number=data.get("vehicle_number"),
        brand=data.get("brand"),
        model=data.get("model"),
        max_weight=data.get("max_weight")
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