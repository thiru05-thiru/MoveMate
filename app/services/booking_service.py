from datetime import datetime

from extensions import db
from app.models.booking import Booking
from app.models.driver import Driver
from app.models.user import User
from app.services.driver_service import find_nearest_driver
from app.models.vehicle import Vehicle


def generate_booking_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"MM{timestamp}"


def create_booking(customer_id, data):

    # Find nearest driver
    nearest_driver = find_nearest_driver(
        pickup_latitude=data["pickup_lat"],
        pickup_longitude=data["pickup_lng"]
    )

    booking = Booking(
        booking_id=generate_booking_id(),
        customer_id=customer_id,

        pickup_address=data["pickup_address"],
        destination_address=data["destination_address"],

        pickup_lat=data["pickup_lat"],
        pickup_lng=data["pickup_lng"],

        destination_lat=data["destination_lat"],
        destination_lng=data["destination_lng"],

        vehicle_type=data["vehicle_type"],
        goods_type=data["goods_type"],
        estimated_weight=data["estimated_weight"]
    )

    # Driver found
    if nearest_driver:

        booking.driver_id = nearest_driver["driver_id"]
        booking.vehicle_id = nearest_driver["vehicle_id"]
        booking.status = "Driver Assigned"

    else:

        booking.status = "Waiting for Driver"

    db.session.add(booking)
    db.session.commit()

    return booking


def get_customer_bookings(customer_id):
    return Booking.query.filter_by(
        customer_id=customer_id
    ).order_by(
        Booking.created_at.desc()
    ).all()

def get_driver_bookings(driver_user_id):
    """
    Returns all bookings assigned to the logged-in driver.
    """

    from app.models.driver import Driver

    driver = Driver.query.filter_by(
        user_id=driver_user_id
    ).first()

    if not driver:
        return []

    bookings = Booking.query.filter_by(
        driver_id=driver.id
    ).order_by(
        Booking.created_at.desc()
    ).all()

    return bookings

def get_booking_by_id(customer_id, booking_id):
    booking = Booking.query.filter_by(
        booking_id=booking_id,
        customer_id=customer_id
    ).first()

    return booking

def get_tracking_details(booking_id):
    """
    Returns tracking information for a booking.
    """

    booking = Booking.query.filter_by(
        booking_id=booking_id
    ).first()

    if not booking:
        return None

    response = {
        "booking_id": booking.booking_id,
        "status": booking.status,

        "pickup_address": booking.pickup_address,
        "destination_address": booking.destination_address,

        # Pickup Coordinates
        "pickup_lat": booking.pickup_lat,
        "pickup_lng": booking.pickup_lng,

        # Destination Coordinates
        "destination_lat": booking.destination_lat,
        "destination_lng": booking.destination_lng,

        "driver": None,
        "vehicle": None,
        "driver_location": None,
    }

    if booking.driver_id:

        driver = Driver.query.filter_by(
            id=booking.driver_id
        ).first()

        if driver:

            user = User.query.filter_by(
                id=driver.user_id
            ).first()

            vehicle = Vehicle.query.filter_by(
                id=booking.vehicle_id
            ).first()

            response["driver"] = {
                "name": user.full_name if user else "",
                "phone": user.phone if user else "",
            }

            if vehicle:
                response["vehicle"] = {
                    "type": vehicle.vehicle_type,
                    "number": vehicle.vehicle_number,
                }

            response["driver_location"] = {
                "latitude": driver.latitude,
                "longitude": driver.longitude,
            }

    return response

def cancel_booking(customer_id, booking_id):
    booking = Booking.query.filter_by(
        booking_id=booking_id,
        customer_id=customer_id
    ).first()

    if booking is None:
        return None

    # Don't allow cancelling a completed booking
    if booking.status == "Delivered":
        return "DELIVERED"

    booking.status = "Cancelled"

    db.session.commit()

    return booking

def accept_booking(driver_user_id, booking_id):
    """
    Driver accepts an assigned booking.
    """

    from app.models.driver import Driver

    print("JWT User ID:", driver_user_id)

    driver = Driver.query.filter_by(user_id=driver_user_id).first()

    print("Driver:", driver)

    if not driver:
        return None, "Driver not found."

    booking = Booking.query.filter_by(
        booking_id=booking_id,
        driver_id=driver.id
    ).first()

    if not booking:
        return None, "Booking not found."

    if booking.status != "Driver Assigned":
        return None, f"Booking cannot be accepted. Current status: {booking.status}"

    booking.status = "Accepted"

    db.session.commit()

    return booking, None


def start_trip(driver_user_id, booking_id):
    """
    Driver starts the trip.
    """

    from app.models.driver import Driver

    driver = Driver.query.filter_by(user_id=driver_user_id).first()

    if not driver:
        return None, "Driver not found."

    booking = Booking.query.filter_by(
        booking_id=booking_id,
        driver_id=driver.id
    ).first()

    if not booking:
        return None, "Booking not found."

    if booking.status != "Accepted":
        return None, f"Trip cannot be started. Current status: {booking.status}"

    booking.status = "In Transit"

    db.session.commit()

    return booking, None

def deliver_trip(driver_user_id, booking_id):
    """
    Driver marks the trip as delivered.
    """

    from app.models.driver import Driver

    driver = Driver.query.filter_by(user_id=driver_user_id).first()

    if not driver:
        return None, "Driver not found."

    booking = Booking.query.filter_by(
        booking_id=booking_id,
        driver_id=driver.id
    ).first()

    if not booking:
        return None, "Booking not found."

    if booking.status != "In Transit":
        return None, f"Trip cannot be delivered. Current status: {booking.status}"

    booking.status = "Delivered"

    db.session.commit()

    return booking, None