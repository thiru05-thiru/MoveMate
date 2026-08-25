from extensions import db
from datetime import datetime
from bson import ObjectId

class DriverHelper:
    @staticmethod
    def create_driver(user_id, data):
        driver_doc = {
            "user_id": user_id,
            "license_number": data.get('license_number'),
            "aadhaar_number": data.get('aadhaar_number'),
            "pan_number": data.get('pan_number'),
            "license_proof": data.get('license_proof'),
            "aadhaar_proof": data.get('aadhaar_proof'),
            "pan_proof": data.get('pan_proof'),
            "status": "Pending",
            "verification_status": "Pending",
            "is_online": False,
            "latitude": None,
            "longitude": None,
            "rating": 5.0,
            "total_trips": 0,
            "created_at": datetime.utcnow()
        }
        result = db.drivers.insert_one(driver_doc)

        # Create Vehicle
        vehicle_doc = {
            "driver_id": str(result.inserted_id),
            "vehicle_type": data.get('vehicle_type'),
            "vehicle_number": data.get('vehicle_number'),
            "brand": data.get('brand'),
            "model": data.get('model'),
            "max_weight": data.get('max_weight'),
            "rc_number": data.get('rc_number'),
            "insurance_number": data.get('insurance_number'),
            "fc_expiry": data.get('fc_expiry'),
            "rc_proof": data.get('rc_proof'),
            "insurance_proof": data.get('insurance_proof'),
            "status": "Available",
            "created_at": datetime.utcnow()
        }
        db.vehicles.insert_one(vehicle_doc)

        return str(result.inserted_id)

    @staticmethod
    def get_by_user_id(user_id):
        driver = db.drivers.find_one({"user_id": user_id})
        if driver:
            driver['_id'] = str(driver['_id'])
        return driver
