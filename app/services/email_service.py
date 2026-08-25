import random
import logging
import threading
from flask import current_app
from flask_mail import Message
from extensions import mail, db
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_async_email(app, msg, recipient, otp):
    with app.app_context():
        try:
            logger.info(f"Background thread: Attempting to send mail to {recipient}...")
            mail.send(msg)
            logger.info(f"✅ Background thread: OTP sent to {recipient}")
        except BaseException as e:
            logger.error(f"❌ Background thread: SMTP delivery failed for {recipient}: {str(e)}")
            # We don't need to do anything here because the Rescue Mode log already happened

def send_otp_email(user_doc):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    recipient = user_doc.get('email')
    if not recipient:
        logger.error("OTP Error: Recipient email missing from user_doc")
        return False, "Recipient email missing"

    try:
        # Update MongoDB immediately
        db.users.update_one(
            {"email": recipient},
            {"$set": {"otp_code": otp, "otp_expiry": expiry}}
        )

        # Log OTP IMMEDIATELY for Rescue Mode (before any network calls)
        logger.info(f"🚨 RESCUE MODE: OTP for {recipient} is [{otp}]")

        msg = Message(
            subject="Your MoveMate Verification Code",
            recipients=[recipient],
            body=f"Hello {user_doc.get('full_name', 'User')},\n\nYour code is: {otp}\n\nExpires in 5 mins."
        )

        # Send email in a separate thread so it doesn't block the API response
        # This prevents "Network Error" if the SMTP server is slow or crashing
        app = current_app._get_current_object()
        threading.Thread(target=send_async_email, args=(app, msg, recipient, otp)).start()

        return True, None
    except Exception as e:
        logger.error(f"❌ ERROR in send_otp_email: {str(e)}")
        return True, "Fallback triggered"
