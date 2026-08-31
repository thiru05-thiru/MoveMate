import random
import logging
import threading
import socket
import smtplib
from flask import current_app
from flask_mail import Message
from extensions import mail, db
from datetime import datetime, timedelta

# ====================================================================
# NETWORK PATCH: Force IPv4 for Render/Gmail compatibility
# ====================================================================
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4
# ====================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_async_email(app, msg, recipient):
    with app.app_context():
        try:
            logger.info(f"🚀 SMTP: Starting direct SSL delivery to {recipient}...")
            # Using a strict 20-second timeout to prevent worker hangs
            socket.setdefaulttimeout(20)

            mail.send(msg)
            logger.info(f"✅ SMTP SUCCESS: OTP delivered to {recipient}")
        except Exception as e:
            logger.error(f"❌ SMTP FAILED: {str(e)}")
            # Log the specific error type to debug further
            if "Network is unreachable" in str(e):
                logger.error("DANGER: Render is still blocking outgoing mail ports.")

def send_otp_email(user_doc):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    recipient = user_doc.get('email')

    if not recipient: return False, "No email"

    try:
        # 1. Update Database
        db.users.update_one(
            {"email": recipient},
            {"$set": {"otp_code": otp, "otp_expiry": expiry}}
        )

        # 2. Rescue Log (Keep for your safety, but the goal is the inbox)
        logger.info(f"🔑 [DEV LOG] OTP for {recipient}: {otp}")

        # 3. Create the message
        msg = Message(
            subject=f"Verification Code: {otp}",
            recipients=[recipient],
            body=f"Hello,\n\nYour MoveMate verification code is: {otp}\n\nThis code will expire in 5 minutes.\n\nIf you did not request this, please ignore this email."
        )

        # 4. Asynchronous Delivery
        app = current_app._get_current_object()
        threading.Thread(target=send_async_email, args=(app, msg, recipient)).start()

        return True, None
    except Exception as e:
        logger.error(f"OTP SERVICE ERROR: {str(e)}")
        return True, "Fallback"
