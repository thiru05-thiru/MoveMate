from app import db
from datetime import datetime


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("drivers.id"),
        nullable=False
    )

    vehicle_type = db.Column(db.String(50), nullable=False)

    vehicle_number = db.Column(db.String(30), unique=True, nullable=False)

    brand = db.Column(db.String(50))

    model = db.Column(db.String(50))

    max_weight = db.Column(db.Float)

    rc_image = db.Column(db.String(255))

    insurance_image = db.Column(db.String(255))

    status = db.Column(
        db.String(20),
        default="Available"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )