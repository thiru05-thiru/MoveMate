import random
import logging
import socket
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from extensions import mail, db

# ====================================================================
# NETWORK COMPATIBILITY PATCH
# Forces IPv4 to prevent "Network Unreachable" on Render/Cloud
# ====================================================================
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4
# ====================================================================

logger = logging.getLogger(__name__)

class OTPService:
    @staticmethod
    def generate_code():
        """Generates a secure 6-digit OTP."""
        return str(random.randint(100000, 999999))

    @staticmethod
    def create_otp(email):
        """Generates OTP, saves to DB with expiry, and returns it."""
        code = OTPService.generate_code()
        expiry = datetime.utcnow() + timedelta(minutes=5)

        try:
            db.users.update_one(
                {"email": email.strip().lower()},
                {"$set": {
                    "otp_code": code,
                    "otp_expiry": expiry
                }}
            )
            logger.info(f"OTP created and stored for {email}")
            return code
        except Exception as e:
            logger.error(f"Failed to store OTP for {email}: {str(e)}")
            return None

    @staticmethod
    def send_email(email, code, full_name="User"):
        """Synchronously sends the OTP email via SMTP."""
        try:
            msg = Message(
                subject=f"Your MoveMate Login Code: {code}",
                recipients=[email.strip().lower()],
                body=f"Hello {full_name},\n\nYour MoveMate verification code is: {code}\n\nThis code is valid for 5 minutes. Do not share it with anyone."
            )

            # Set a socket timeout to prevent hanging the whole request
            socket.setdefaulttimeout(15)

            logger.info(f"Attempting SMTP delivery to {email}...")
            mail.send(msg)
            logger.info(f"✅ OTP email delivered successfully to {email}")
            return True, None

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ SMTP Error for {email}: {error_msg}")
            return False, error_msg

    @staticmethod
    def verify_otp(email, input_code):
        """Validates OTP code and expiry. Returns (Success, Message)."""
        user = db.users.find_one({"email": email.strip().lower()})

        if not user:
            return False, "User not found"

        stored_code = user.get('otp_code')
        expiry = user.get('otp_expiry')

        if not stored_code or stored_code != input_code:
            return False, "Invalid verification code"

        if not expiry or datetime.utcnow() > expiry:
            return False, "Code has expired. Please request a new one."

        # Clear OTP after successful verification
        db.users.update_one(
            {"email": email},
            {"$set": {"otp_code": None, "otp_expiry": None}}
        )

        return True, "Verified"
