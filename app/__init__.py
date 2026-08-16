from flask import Flask
from config import Config
from extensions import jwt, cors, mail, init_mongodb

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)

    # Initialize MongoDB
    with app.app_context():
        init_mongodb(app)

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.booking import booking_bp
    from app.routes.driver import driver_bp
    from app.routes.payment import payment_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(driver_bp, url_prefix="/api/drivers")
    app.register_blueprint(payment_bp, url_prefix="/api/payments")

    return app
