import random
from flask_mail import Message
from extensions import mail, db
from datetime import datetime, timedelta
from app.models.user import User

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user):
    """
    Generates an OTP, saves it to the user record, and sends it via email.
    """
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()

    msg = Message(
        subject="Your MoveMate Verification Code",
        recipients=[user.email],
        body=f"Hello {user.full_name},\n\nYour 6-digit verification code is: {otp}\n\nThis code will expire in 5 minutes.\n\nSafe moving,\nThe MoveMate Team"
    )

    try:
        mail.send(msg)
        return True, "OTP sent successfully"
    except Exception as e:
        print(f"Mail send error: {str(e)}")
        return False, f"Failed to send email: {str(e)}"
