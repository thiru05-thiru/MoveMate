import random
from flask_mail import Message
from extensions import mail, db
from datetime import datetime, timedelta

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_doc):
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    # Update MongoDB
    db.users.update_one(
        {"email": user_doc['email']},
        {"$set": {"otp_code": otp, "otp_expiry": expiry}}
    )

    msg = Message(
        subject="Your MoveMate Verification Code",
        recipients=[user_doc['email']],
        body=f"Hello {user_doc['full_name']},\n\nYour code is: {otp}\n\nExpires in 5 mins."
    )

    try:
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)
