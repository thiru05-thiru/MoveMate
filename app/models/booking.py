from datetime import datetime
from extensions import db

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(db.String(20), unique=True, nullable=False)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("drivers.id"),
        nullable=True
    )

    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey("vehicles.id"),
        nullable=True
    )

    pickup_address = db.Column(db.Text, nullable=False)
    destination_address = db.Column(db.Text, nullable=False)

    pickup_lat = db.Column(db.Float)
    pickup_lng = db.Column(db.Float)

    destination_lat = db.Column(db.Float)
    destination_lng = db.Column(db.Float)

    vehicle_type = db.Column(db.String(50))
    goods_type = db.Column(db.String(100))
    estimated_weight = db.Column(db.Float)

    distance = db.Column(db.Float)
    estimated_price = db.Column(db.Float)

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )