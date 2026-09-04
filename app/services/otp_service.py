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
        """Synchronously sends the professional HTML OTP email via SMTP."""
        try:
            subject = f"Your MoveMate verification code: {code}"
            recipient = email.strip().lower()

            # Professional HTML Template (Vercel/Google Style)
            html_body = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 450px; margin: 40px auto; padding: 32px; border: 1px solid #eaeaea; border-radius: 8px; color: #000; background-color: #ffffff;">
                <div style="margin-bottom: 24px; text-align: left;">
                    <span style="font-size: 28px; font-weight: 900; color: #000;">▲</span>
                    <span style="font-size: 24px; font-weight: 700; vertical-align: middle; margin-left: 8px; letter-spacing: -0.5px;">MoveMate</span>
                </div>

                <h2 style="font-size: 20px; font-weight: 600; margin: 0 0 12px 0; color: #111827;">Sign up for MoveMate</h2>
                <p style="font-size: 14px; color: #666; margin: 0 0 24px 0; line-height: 1.6;">
                    A login request was made for your account. Please use the verification code below to finish signing in.
                </p>

                <div style="background-color: #f6f6f6; border-radius: 6px; padding: 24px; text-align: center; margin-bottom: 24px;">
                    <span style="font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #000; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;">{code}</span>
                </div>

                <p style="font-size: 13px; color: #888; margin: 0 0 24px 0;">
                    This code expires in <span style="color: #000; font-weight: 500;">5 minutes</span>.
                </p>

                <p style="font-size: 12px; color: #999; margin: 0; line-height: 1.5; border-top: 1px solid #eaeaea; padding-top: 24px;">
                    By signing up, you agree to our <a href="#" style="color: #000; text-decoration: none; font-weight: 500;">Terms of Service</a> and <a href="#" style="color: #000; text-decoration: none; font-weight: 500;">Privacy Policy</a>.
                </p>
            </div>
            """

            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=html_body,
                body=f"Your MoveMate verification code is: {code}" # Text fallback
            )

            # Set a longer socket timeout (30s) for slow cloud connections
            socket.setdefaulttimeout(30)

            logger.info(f"Attempting SMTP delivery to {recipient} via Port 465...")
            mail.send(msg)
            logger.info(f"✅ OTP email delivered successfully to {recipient}")
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
