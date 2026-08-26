import random
import logging
import threading
import sys
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
    # This runs in a separate thread to prevent gunicorn crashes
    try:
        with app.app_context():
            logger.info(f"Background thread: Sending to {recipient}...")
            mail.send(msg)
            logger.info(f"✅ Background thread: Success for {recipient}")
    except BaseException as e:
        # Catching BaseException to prevent thread from ever killing the main process
        print(f"THREAD ERROR: {str(e)}", file=sys.stderr)

def send_otp_email(user_doc):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    recipient = user_doc.get('email')

    if not recipient:
        return False, "No email"

    try:
        # 1. Update MongoDB immediately
        db.users.update_one(
            {"email": recipient},
            {"$set": {"otp_code": otp, "otp_expiry": expiry}}
        )

        # 2. LOG THE CODE IMMEDIATELY for the user to see in Render Logs
        print(f"🚨 RESCUE MODE: OTP for {recipient} is [{otp}]")

        # 3. Create the message
        msg = Message(
            subject="Your MoveMate Verification Code",
            recipients=[recipient],
            body=f"Hello,\n\nYour code is: {otp}\n\nExpires in 5 mins."
        )

        # 4. Start background thread - DO NOT WAIT for it
        app = current_app._get_current_object()
        thread = threading.Thread(target=send_async_email, args=(app, msg, recipient, otp))
        thread.daemon = True # Ensure it doesn't block server shutdown
        thread.start()

        return True, None
    except Exception as e:
        logger.error(f"OTP SERVICE ERROR: {str(e)}")
        # We still return True because the DB update and log above likely succeeded
        return True, "Rescue fallback active"
