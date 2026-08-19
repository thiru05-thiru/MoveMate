from extensions import db
from datetime import datetime

class PaymentHelper:
    @staticmethod
    def create(booking_id, order_id, amount, platform_fee, driver_share):
        payment_doc = {
            "booking_id": booking_id,
            "razorpay_order_id": order_id,
            "razorpay_payment_id": None,
            "razorpay_signature": None,
            "amount": amount,
            "platform_fee": platform_fee,
            "driver_share": driver_share,
            "status": "Pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db.payments.insert_one(payment_doc)
        return payment_doc

    @staticmethod
    def get_by_order_id(order_id):
        return db.payments.find_one({"razorpay_order_id": order_id})

    @staticmethod
    def update_status(order_id, payment_id, signature, status):
        db.payments.update_one(
            {"razorpay_order_id": order_id},
            {"$set": {
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
                "status": status,
                "updated_at": datetime.utcnow()
            }}
        )
