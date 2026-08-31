import random
import logging
import threading
import socket
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

def send_async_email(app, msg, recipient, otp):
    with app.app_context():
        try:
            logger.info(f"SMTP Thread: Connecting to Gmail for {recipient}...")
            mail.send(msg)
            logger.info(f"✅ SMTP SUCCESS: Mail sent to {recipient}")
        except Exception as e:
            logger.error(f"❌ SMTP FATAL ERROR: {str(e)}")

def send_otp_email(user_doc):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    recipient = user_doc.get('email')

    if not recipient: return False, "No email"

    try:
        # 1. Store in DB
        db.users.update_one(
            {"email": recipient},
            {"$set": {"otp_code": otp, "otp_expiry": expiry}}
        )

        # 2. Log for Developer (Rescue Mode stays as a backup)
        logger.info(f"🔑 OTP GENERATED: {recipient} -> {otp}")

        # 3. Prepare Message
        msg = Message(
            subject=f"{otp} is your MoveMate verification code",
            recipients=[recipient],
            body=f"Your MoveMate verification code is: {otp}\n\nValid for 5 minutes."
        )

        # 4. Background Delivery
        app = current_app._get_current_object()
        threading.Thread(target=send_async_email, args=(app, msg, recipient, otp)).start()

        return True, None
    except Exception as e:
        logger.error(f"SERVICE ERROR: {str(e)}")
        return True, "Fallback"
