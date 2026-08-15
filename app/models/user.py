from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(15), unique=True)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="customer")

    # 2FA Fields
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)