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

        # Professional HTML Template (Luxury Teal & Rose Gold Theme)
        html_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 450px; margin: 40px auto; padding: 40px; border: 1px solid #eaeaea; border-radius: 20px; color: #000; background-color: #ffffff; box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
            <div style="margin-bottom: 32px; text-align: center;">
                <div style="width: 50px; height: 50px; background-color: #0f766e; border-radius: 12px; display: inline-block; line-height: 50px; text-align: center;">
                    <span style="color: #d9a08b; font-size: 24px; font-weight: 900;">Z</span>
                </div>
                <div style="font-size: 20px; font-weight: 900; color: #0f766e; margin-top: 12px; text-transform: uppercase; letter-spacing: 2px;">Zoventra Supreme</div>
            </div>

            <h2 style="font-size: 22px; font-weight: 700; margin: 0 0 16px 0; color: #111827; text-align: center;">Identity Verification</h2>
            <p style="font-size: 14px; color: #64748b; margin: 0 0 32px 0; line-height: 1.6; text-align: center;">
                A sign-in attempt requires a secure terminal key. Please use the authorization code below.
            </p>

            <div style="background-color: #f8fafc; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px; border: 1px solid #f1f5f9;">
                <span style="font-size: 42px; font-weight: 900; letter-spacing: 15px; color: #0f766e; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;">{code}</span>
            </div>

            <p style="font-size: 13px; color: #94a3b8; margin: 0 0 24px 0; text-align: center;">
                Valid for <span style="color: #0f766e; font-weight: 700;">5 minutes</span>. Secured by Zoventra Supreme Protocol.
            </p>

            <div style="border-top: 1px solid #f1f5f9; padding-top: 24px; text-align: center;">
                <p style="font-size: 11px; color: #cbd5e1; margin: 0; line-height: 1.5; text-transform: uppercase; letter-spacing: 1px;">
                    &copy; 2026 Zoventra Supreme Logistics<br>
                    Global Command Center • Bangalore, India
                </p>
            </div>
        </div>
        """

        # Resend API Data
        # Note: If you don't have a verified domain, Resend requires sending
        # from 'onboarding@resend.dev' to your own email only.
        data = {
            "from": "Zoventra <onboarding@resend.dev>",
            "to": [email],
            "subject": f"{code} is your Zoventra verification code",
            "html": html_content
        }

        try:
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Zoventra-App/1.0"
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
