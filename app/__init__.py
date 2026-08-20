from flask import Flask, jsonify
from config import Config
from extensions import jwt, cors, mail, init_mongodb

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Apply Extensions
    jwt.init_app(app)
    mail.init_app(app)

    # Configure CORS to be very permissive for development and errors
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize MongoDB
    with app.app_context():
        init_mongodb(app)

    # Global Error Handler to ensure CORS is always sent
    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"CRASH DETECTED: {str(e)}")
        response = jsonify({
            "success": False,
            "message": "Internal Server Error",
            "details": str(e)
        })
        response.status_code = 500
        # Manual CORS header injection for crashes
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

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
