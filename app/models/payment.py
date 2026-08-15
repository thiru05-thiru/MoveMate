from extensions import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), db.ForeignKey("bookings.booking_id"), nullable=False)
    razorpay_order_id = db.Column(db.String(100), unique=True, nullable=False)
    razorpay_payment_id = db.Column(db.String(100), unique=True, nullable=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)

    amount = db.Column(db.Float, nullable=False)  # Total amount paid by customer
    platform_fee = db.Column(db.Float, nullable=False)  # 30% of total
    driver_share = db.Column(db.Float, nullable=False)  # 70% of total

    status = db.Column(db.String(20), default="Pending") # Pending, Captured, Failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "platform_fee": self.platform_fee,
            "driver_share": self.driver_share,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
