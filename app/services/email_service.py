import random
import logging
from flask_mail import Message
from extensions import mail, db
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_doc):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    recipient = user_doc.get('email')
    if not recipient:
        logger.error("OTP Error: Recipient email missing from user_doc")
        return False, "Recipient email missing"

    try:
        # Update MongoDB
        db.users.update_one(
            {"email": recipient},
            {"$set": {"otp_code": otp, "otp_expiry": expiry}}
        )

        msg = Message(
            subject="Your MoveMate Verification Code",
            recipients=[recipient],
            body=f"Hello {user_doc.get('full_name', 'User')},\n\nYour code is: {otp}\n\nExpires in 5 mins."
        )

        logger.info(f"Attempting to send OTP email to {recipient}...")
        mail.send(msg)
        logger.info(f"OTP sent successfully to {recipient}")
        return True, None
    except Exception as e:
        logger.error(f"Failed to send OTP to {recipient}: {str(e)}")
        return False, str(e)
