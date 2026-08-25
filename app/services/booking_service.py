from datetime import datetime
from extensions import db
from app.models.booking import BookingHelper
from app.services.driver_service import find_nearest_driver
from bson import ObjectId

def create_booking(customer_id, data):
    # Find nearest driver
    nearest_driver = None
    try:
        nearest_driver = find_nearest_driver(
            pickup_latitude=data["pickup_lat"],
            pickup_longitude=data["pickup_lng"],
            vehicle_type=data.get("vehicle_type")
        )
    except Exception as e:
        print(f"Nearest driver search failed: {e}")

    # Create the booking document
    booking = BookingHelper.create(customer_id, data, nearest_driver)
    return booking


def get_customer_bookings(customer_id):
    return BookingHelper.get_customer_bookings(customer_id)

def get_driver_bookings(driver_user_id):
    """
    Returns all bookings assigned to the logged-in driver or broadcasts matching vehicle type.
    """
    driver = db.drivers.find_one({"user_id": driver_user_id})
    if not driver:
        return []

    vehicle = db.vehicles.find_one({"driver_id": str(driver['_id'])})
    vehicle_type = vehicle['vehicle_type'] if vehicle else None

    # Find jobs assigned to this driver OR waiting jobs that match this driver's vehicle
    query = {
        "$or": [
            {"driver_id": str(driver['_id'])},
            {
                "status": "Waiting for Driver",
                "vehicle_type": vehicle_type
            }
        ]
    }

    bookings = list(db.bookings.find(query).sort("created_at", -1))

    booking_list = []
    for b in bookings:
        b['_id'] = str(b['_id'])
        b['created_at'] = b['created_at'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(b['created_at'], datetime) else b['created_at']
        booking_list.append(b)

    return booking_list

def get_booking_by_id(customer_id, booking_id):
    booking = db.bookings.find_one({
        "booking_id": booking_id,
        "customer_id": customer_id
    })
    if booking:
        booking['_id'] = str(booking['_id'])
    return booking

def get_tracking_details(booking_id):
    booking = db.bookings.find_one({"booking_id": booking_id})
    if not booking:
        return None

    response = {
        "booking_id": booking['booking_id'],
        "status": booking['status'],
        "pickup_address": booking['pickup_address'],
        "destination_address": booking['destination_address'],
        "pickup_lat": booking['pickup_lat'],
        "pickup_lng": booking['pickup_lng'],
        "destination_lat": booking['destination_lat'],
        "destination_lng": booking['destination_lng'],
        "driver": None,
        "vehicle": None,
        "driver_location": None,
    }

    if booking.get('driver_id'):
        driver = db.drivers.find_one({"_id": ObjectId(booking['driver_id'])})
        if driver:
            user = db.users.find_one({"_id": ObjectId(driver['user_id'])})
            vehicle = db.vehicles.find_one({"_id": ObjectId(booking['vehicle_id'])})

            response["driver"] = {
                "name": user['full_name'] if user else "Unknown",
                "phone": user['phone'] if user else "",
            }

            if vehicle:
                response["vehicle"] = {
                    "type": vehicle['vehicle_type'],
                    "number": vehicle['vehicle_number'],
                }

            response["driver_location"] = {
                "latitude": driver.get('latitude'),
                "longitude": driver.get('longitude'),
            }

    return response

def cancel_booking(customer_id, booking_id):
    booking = db.bookings.find_one({
        "booking_id": booking_id,
        "customer_id": customer_id
    })

    if not booking:
        return None

    if booking['status'] == "Delivered":
        return "DELIVERED"

    db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {"status": "Cancelled", "updated_at": datetime.utcnow()}}
    )

    return {"status": "Cancelled"}

def accept_booking(driver_user_id, booking_id):
    driver = db.drivers.find_one({"user_id": driver_user_id})
    if not driver:
        return None, "Driver not found."

    booking = db.bookings.find_one({
        "booking_id": booking_id,
        "driver_id": str(driver['_id'])
    })

    if not booking:
        return None, "Booking not found."

    if booking['status'] != "Driver Assigned":
        return None, f"Booking cannot be accepted. Current status: {booking['status']}"

    db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {"status": "Awaiting Payment", "updated_at": datetime.utcnow()}}
    )

    return {"booking_id": booking_id, "status": "Awaiting Payment"}, None


def start_trip(driver_user_id, booking_id):
    driver = db.drivers.find_one({"user_id": driver_user_id})
    if not driver:
        return None, "Driver not found."

    booking = db.bookings.find_one({
        "booking_id": booking_id,
        "driver_id": str(driver['_id'])
    })

    if not booking:
        return None, "Booking not found."

    if booking['status'] != "Paid":
        return None, f"Trip cannot be started. Customer has not paid yet. Current status: {booking['status']}"

    db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {"status": "In Transit", "updated_at": datetime.utcnow()}}
    )

    return {"booking_id": booking_id, "status": "In Transit"}, None

def deliver_trip(driver_user_id, booking_id):
    driver = db.drivers.find_one({"user_id": driver_user_id})
    if not driver:
        return None, "Driver not found."

    booking = db.bookings.find_one({
        "booking_id": booking_id,
        "driver_id": str(driver['_id'])
    })

    if not booking:
        return None, "Booking not found."

    if booking['status'] != "In Transit":
        return None, f"Trip cannot be delivered. Current status: {booking['status']}"

    db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {"status": "Delivered", "updated_at": datetime.utcnow()}}
    )

    return {"booking_id": booking_id, "status": "Delivered"}, None
