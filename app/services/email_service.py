import random
import logging
import socket
from flask import current_app
from flask_mail import Message
from extensions import mail, db
from datetime import datetime, timedelta

# Network Patch: Force IPv4 to bypass Render networking blocks
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_doc):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    recipient = user_doc.get('email')

    if not recipient: return False, "No email"

    try:
        # 1. Store OTP in Database
        db.users.update_one(
            {"email": recipient},
            {"$set": {"otp_code": otp, "otp_expiry": expiry}}
        )

        # 2. Prepare the Inbox-Ready Message
        msg = Message(
            subject=f"Your MoveMate Verification Code: {otp}",
            recipients=[recipient],
            body=f"Hello,\n\nYour MoveMate verification code is: {otp}\n\nValid for 5 minutes."
        )

        # 3. Direct Delivery (Not in background to ensure Gunicorn doesn't kill it)
        logger.info(f"📤 SENDING REAL EMAIL to {recipient}...")

        # Short timeout to keep the app fast
        socket.setdefaulttimeout(15)
        mail.send(msg)

        logger.info(f"✅ EMAIL DELIVERED SUCCESSFULLY TO INBOX: {recipient}")
        return True, None

    except Exception as e:
        logger.error(f"❌ MAIL DELIVERY FAILED: {str(e)}")
        # Log the code in logs so you aren't locked out if Gmail is down
        logger.info(f"🔑 BACKUP LOG: OTP for {recipient} is [{otp}]")
        return True, "Fallback"
