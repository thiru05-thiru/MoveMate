from datetime import datetime

from extensions import db
from app.models.booking import Booking


def generate_booking_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"MM{timestamp}"


def create_booking(customer_id, data):
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
        estimated_weight=data["estimated_weight"],

        status="Pending"
    )

    db.session.add(booking)
    db.session.commit()

    return booking


def get_customer_bookings(customer_id):
    return Booking.query.filter_by(
        customer_id=customer_id
    ).order_by(
        Booking.created_at.desc()
    ).all()

def get_booking_by_id(customer_id, booking_id):
    booking = Booking.query.filter_by(
        booking_id=booking_id,
        customer_id=customer_id
    ).first()

    return booking

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