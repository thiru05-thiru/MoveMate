from app.models.driver import DriverHelper
from app.utils.distance import haversine_distance
from extensions import db
from bson import ObjectId
from datetime import datetime

def register_driver(
    user_id,
    license_number,
    aadhaar_number,
    pan_number,
    vehicle_type,
    vehicle_number,
    brand,
    model,
    max_weight,
    rc_number
):
    # Check if the user is already registered as a driver
    if DriverHelper.get_by_user_id(user_id):
        return None, "You are already registered as a driver."

    # Check if the vehicle number already exists
    if db.vehicles.find_one({"vehicle_number": vehicle_number}):
        return None, "Vehicle number already exists."

    driver_id = DriverHelper.create_driver(user_id, {
        "license_number": license_number,
        "aadhaar_number": aadhaar_number,
        "pan_number": pan_number,
        "vehicle_type": vehicle_type,
        "vehicle_number": vehicle_number,
        "brand": brand,
        "model": model,
        "max_weight": max_weight,
        "rc_number": rc_number
    })

    return {"driver_id": driver_id}, None


# =====================================
# Driver Availability Services
# =====================================

def go_online(user_id):
    result = db.drivers.update_one(
        {"user_id": user_id},
        {"$set": {"is_online": True}}
    )
    if result.matched_count == 0:
        return None, "Driver not found."
    return {"user_id": user_id, "is_online": True}, None


def go_offline(user_id):
    result = db.drivers.update_one(
        {"user_id": user_id},
        {"$set": {"is_online": False}}
    )
    if result.matched_count == 0:
        return None, "Driver not found."
    return {"user_id": user_id, "is_online": False}, None


def get_driver_status(user_id):
    driver = DriverHelper.get_by_user_id(user_id)
    if not driver:
        return None, "Driver not found."
    return {
        "driver_id": driver['_id'],
        "is_online": driver.get('is_online', False),
        "status": driver.get('status', 'Pending')
    }, None

# =====================================
# Driver Location Services
# =====================================

def update_driver_location(user_id, latitude, longitude):
    result = db.drivers.update_one(
        {"user_id": user_id},
        {"$set": {"latitude": latitude, "longitude": longitude}}
    )
    if result.matched_count == 0:
        return None, "Driver not found."
    return {"user_id": user_id, "latitude": latitude, "longitude": longitude}, None


def get_driver_location(user_id):
    driver = DriverHelper.get_by_user_id(user_id)
    if not driver:
        return None, "Driver not found."
    return {
        "driver_id": driver['_id'],
        "latitude": driver.get('latitude'),
        "longitude": driver.get('longitude')
    }, None

# =====================================
# Find Available Drivers
# =====================================

def get_available_drivers():
    drivers = list(db.drivers.find({
        "is_online": True,
        "status": {"$in": ["Pending", "Approved"]},
        "latitude": {"$ne": None},
        "longitude": {"$ne": None}
    }))

    available_drivers = []
    for driver in drivers:
        vehicle = db.vehicles.find_one({"driver_id": str(driver['_id'])})
        available_drivers.append({
            "driver_id": str(driver['_id']),
            "user_id": driver['user_id'],
            "vehicle_id": str(vehicle['_id']) if vehicle else None,
            "vehicle_type": vehicle['vehicle_type'] if vehicle else None,
            "latitude": driver['latitude'],
            "longitude": driver['longitude'],
            "status": driver['status']
        })
    return available_drivers

# =====================================
# Find Nearest Driver
# =====================================

def find_nearest_driver(pickup_latitude, pickup_longitude, vehicle_type=None):
    drivers = get_available_drivers()

    if vehicle_type:
        drivers = [d for d in drivers if d.get('vehicle_type') == vehicle_type]

    if not drivers:
        return None

    for driver in drivers:
        driver["distance_km"] = haversine_distance(
            pickup_latitude,
            pickup_longitude,
            driver["latitude"],
            driver["longitude"]
        )

    drivers.sort(key=lambda d: d["distance_km"])
    return drivers[0]

# =====================================
# Driver Jobs
# =====================================

def get_driver_jobs(user_id):
    driver = DriverHelper.get_by_user_id(user_id)
    if not driver:
        return None, "Driver not found."

    bookings = list(db.bookings.find({"driver_id": driver['_id']}).sort("created_at", -1))

    jobs = []
    for booking in bookings:
        jobs.append({
            "booking_id": booking['booking_id'],
            "pickup_address": booking['pickup_address'],
            "destination_address": booking['destination_address'],
            "pickup_lat": booking['pickup_lat'],
            "pickup_lng": booking['pickup_lng'],
            "destination_lat": booking['destination_lat'],
            "destination_lng": booking['destination_lng'],
            "vehicle_type": booking['vehicle_type'],
            "goods_type": booking.get('goods_type'),
            "estimated_weight": booking.get('estimated_weight'),
            "status": booking['status'],
            "created_at": booking['created_at'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(booking['created_at'], datetime) else booking['created_at']
        })
    return jobs, None
