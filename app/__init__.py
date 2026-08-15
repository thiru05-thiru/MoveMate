from flask import Flask

from config import Config
from extensions import db, jwt, cors, mail
from app.models import User, Booking, Payment
from app.routes.driver import driver_bp

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.booking import booking_bp
    from app.routes.payment import payment_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(
        booking_bp,
        url_prefix="/api/bookings"
    )
    app.register_blueprint(
        payment_bp,
        url_prefix="/api/payments"
    )

    app.register_blueprint(
        driver_bp,
        url_prefix="/api/drivers"
    )

    

    with app.app_context():

        print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
        print("Creating database...")

        db.create_all()

        print("Database created.")

        from app.models.driver import Driver
        print("Driver Columns:", Driver.__table__.columns.keys())

    return app