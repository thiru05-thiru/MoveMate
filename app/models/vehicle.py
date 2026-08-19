from extensions import db
from datetime import datetime

class VehicleHelper:
    @staticmethod
    def get_by_driver_id(driver_id):
        return db.vehicles.find_one({"driver_id": driver_id})

    @staticmethod
    def get_by_id(vehicle_id):
        from bson import ObjectId
        return db.vehicles.find_one({"_id": ObjectId(vehicle_id)})
