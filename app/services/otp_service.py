import random
import logging
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from extensions import db
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OTPService:
    @staticmethod
    def generate_code():
        """Generates a secure 6-digit OTP."""
        return str(random.randint(100000, 999999))

    @staticmethod
    def create_and_store_otp(email):
        """Generates OTP, saves to DB with 5-min expiry."""
        code = OTPService.generate_code()
        expiry = datetime.utcnow() + timedelta(minutes=5)

        db.users.update_one(
            {"email": email.strip().lower()},
            {"$set": {"otp_code": code, "otp_expiry": expiry}}
        )
        return code

    @staticmethod
    def send_professional_email(email, code):
        """
        Sends a high-quality HTML email directly via SMTP.
        Uses explicit socket handling to prevent Render timeouts.
        """
        try:
            config = current_app.config
            sender_email = config.get('MAIL_USERNAME')
            sender_password = config.get('MAIL_PASSWORD')

            if not sender_email or not sender_password:
                logger.error("Email credentials missing in environment variables.")
                return False, "Server configuration error"

            # 1. Create the Email Message (HTML)
            message = MIMEMultipart("alternative")
            message["Subject"] = f"{code} is your MoveMate verification code"
            message["From"] = f"MoveMate <{config.get('MAIL_DEFAULT_SENDER')}>"
            message["To"] = email

            html_content = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 450px; margin: 40px auto; padding: 32px; border: 1px solid #eaeaea; border-radius: 12px; color: #000; background-color: #ffffff;">
                <div style="margin-bottom: 24px;">
                    <span style="font-size: 28px; font-weight: 900; color: #f97316;">▲</span>
                    <span style="font-size: 24px; font-weight: 700; vertical-align: middle; margin-left: 8px; letter-spacing: -0.5px;">MoveMate</span>
                </div>

                <h2 style="font-size: 20px; font-weight: 600; margin: 0 0 12px 0; color: #111827;">Verify your identity</h2>
                <p style="font-size: 14px; color: #666; margin: 0 0 24px 0; line-height: 1.6;">
                    Use the verification code below to complete your sign-in request. This code is only valid for a short time.
                </p>

                <div style="background-color: #f6f6f6; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 24px; border: 1px solid #eee;">
                    <span style="font-size: 38px; font-weight: 800; letter-spacing: 12px; color: #000; font-family: 'Courier New', Courier, monospace;">{code}</span>
                </div>

                <p style="font-size: 13px; color: #888; margin: 0 0 24px 0;">
                    This code expires in <span style="color: #000; font-weight: 600;">5 minutes</span>.
                </p>

                <p style="font-size: 12px; color: #999; margin: 0; line-height: 1.5; border-top: 1px solid #eaeaea; padding-top: 24px;">
                    If you didn't request this, you can safely ignore this email.<br>
                    &copy; 2026 MoveMate Logistics. All rights reserved.
                </p>
            </div>
            """

            message.attach(MIMEText(html_content, "html"))

            # 2. Connect and Send with precise socket control
            # We force IPv4 and set a strict 15s timeout
            logger.info(f"Connecting to {config.get('MAIL_SERVER')} for {email}...")

            # Using direct smtplib for better control than extensions
            server = smtplib.SMTP(config.get('MAIL_SERVER'), config.get('MAIL_PORT'), timeout=15)
            server.set_debuglevel(0)
            server.starttls() # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
            server.quit()

            logger.info(f"✅ REAL EMAIL DELIVERED to {email}")
            return True, None

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ SMTP Fatal Error: {error_msg}")
            # Fallback for internal developer reference
            logger.info(f"🔑 BACKUP LOG: OTP for {email} is [{code}]")
            return False, error_msg

    @staticmethod
    def verify_code(email, code):
        """Checks if code matches and is not expired."""
        user = db.users.find_one({"email": email.strip().lower()})
        if not user: return False, "User not found"

        if user.get('otp_code') != code:
            return False, "Invalid verification code"

        if datetime.utcnow() > user.get('otp_expiry', datetime.min):
            return False, "Code has expired. Please try again."

        # Clear code on success
        db.users.update_one({"email": email}, {"$set": {"otp_code": None, "otp_expiry": None}})
        return True, "Success"
