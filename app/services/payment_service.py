import razorpay
import os
import logging
from extensions import db
from app.models.payment import Payment
from app.models.booking import Booking

# Set up logging to track backend errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        logger.info("Razorpay client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Razorpay: {str(e)}")

def create_razorpay_order(booking_id, amount):
    if not client:
        logger.warning("Attempted to create order but Razorpay client is not initialized.")
        return None, "Payments are not configured. Please check RAZORPAY_KEY_ID in .env"

    # Minimum amount validation: 100 paise = 1 INR
    if amount < 1:
        return None, "Minimum booking amount is ₹1"

    try:
        data = {
            "amount": int(amount * 100),
            "currency": "INR",
            "receipt": f"receipt_{booking_id}",
            "notes": {"booking_id": booking_id}
        }

        logger.info(f"Creating Razorpay order for Booking {booking_id} with amount {amount}")
        order = client.order.create(data=data)

        # Split: 30% Platform, 70% Driver
        platform_fee = amount * 0.30
        driver_share = amount * 0.70

        payment = Payment(
            booking_id=booking_id,
            razorpay_order_id=order['id'],
            amount=amount,
            platform_fee=platform_fee,
            driver_share=driver_share,
            status="Pending"
        )

        db.session.add(payment)
        db.session.commit()

        return {
            "order_id": order['id'],
            "amount": amount,
            "currency": "INR",
            "key": RAZORPAY_KEY_ID
        }, None

    except Exception as e:
        logger.error(f"Razorpay Order Error: {str(e)}")
        return None, f"Razorpay API Error: {str(e)}"

def verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        client.utility.verify_payment_signature(params_dict)

        payment = Payment.query.filter_by(razorpay_order_id=razorpay_order_id).first()
        if payment:
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = "Captured"

            booking = Booking.query.filter_by(booking_id=payment.booking_id).first()
            if booking:
                booking.status = "Paid"

            db.session.commit()
            return True, "Payment verified successfully"

        return False, "Internal payment record missing"

    except Exception as e:
        logger.error(f"Verification Error: {str(e)}")
        return False, f"Verification Failed: {str(e)}"
