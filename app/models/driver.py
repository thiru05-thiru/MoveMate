from app import db
from datetime import datetime

class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    # Identification Documents
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    aadhaar_number = db.Column(db.String(20), unique=True, nullable=False)
    pan_number = db.Column(db.String(20), unique=True, nullable=True) # New

    status = db.Column(db.String(20), default="Pending") # Pending, Approved, Suspended
    verification_status = db.Column(db.String(20), default="Pending") # New: Pending, Verified, Rejected

    is_online = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    rating = db.Column(db.Float, default=5.0)
    total_trips = db.Column(db.Integer, default=0)

    # Document Images (URLs/Paths)
    profile_photo = db.Column(db.String(255))
    license_image = db.Column(db.String(255))
    aadhaar_image = db.Column(db.String(255))
    pan_image = db.Column(db.String(255)) # New

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    vehicle = db.relationship("Vehicle", backref="driver", uselist=False, cascade="all, delete-orphan")
