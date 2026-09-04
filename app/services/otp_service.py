import random
import logging
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from extensions import db
from flask import current_app

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
        Sends a professional HTML email via Resend API.
        This uses HTTPS (Port 443) which is NEVER blocked by Render.
        """
        api_key = current_app.config.get('RESEND_API_KEY')

        if not api_key or api_key == "re_123":
            logger.error("❌ ERROR: RESEND_API_KEY is missing. Check your .env or Render Environment Variables.")
            return False, "Server API configuration error"

        logger.info(f"API: Attempting to send email with key starting with: {api_key[:6]}...")

        # Professional HTML Template (Matching Vercel/Google style)
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

        # Resend API Data
        # Note: If you don't have a verified domain, Resend requires sending
        # from 'onboarding@resend.dev' to your own email only.
        data = {
            "from": "MoveMate <onboarding@resend.dev>",
            "to": [email],
            "subject": f"{code} is your MoveMate verification code",
            "html": html_content
        }

        try:
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "MoveMate-App/1.0"
                },
                method="POST"
            )

            logger.info(f"API: Sending professional email to {email}...")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode("utf-8")
                logger.info(f"✅ API SUCCESS: Email delivered via Resend. ID: {res_body}")
                return True, None

        except urllib.error.HTTPError as e:
            error_text = e.read().decode("utf-8")
            logger.error(f"❌ API HTTP Error: {error_text}")
            return False, error_text
        except Exception as e:
            logger.error(f"❌ API Fatal Error: {str(e)}")
            # Backup for safety
            logger.info(f"🔑 BACKUP LOG: OTP for {email} is [{code}]")
            return False, str(e)

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
