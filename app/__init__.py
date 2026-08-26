from flask import Flask, jsonify
import os
from config import Config
from extensions import jwt, cors, mail, init_mongodb

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Move CORS to the absolute top of the initialization
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Apply Extensions
    jwt.init_app(app)
    mail.init_app(app)

    print(f"📧 MAIL SYSTEM: Sender set to {app.config.get('MAIL_DEFAULT_SENDER')}")

    @app.after_request
    def add_cors_headers(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    # Initialize MongoDB
    with app.app_context():
        init_mongodb(app)

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Root route for health check
    @app.route("/")
    def home():
        return jsonify({
            "project": "MoveMate",
            "status": "Backend Running Successfully 🚀",
            "version": "2.0"
        }), 200

    # Global Error Handler to ensure CORS is always sent
    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"CRASH DETECTED: {str(e)}")
        # Check if it's a 404 to provide cleaner info
        code = 500
        if hasattr(e, 'code'): code = e.code

        response = jsonify({
            "success": False,
            "message": "Error occurred",
            "details": str(e)
        })
        response.status_code = code
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.booking import booking_bp
    from app.routes.driver import driver_bp
    from app.routes.payment import payment_bp
    from app.routes.user import user_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(driver_bp, url_prefix="/api/drivers")
    app.register_blueprint(payment_bp, url_prefix="/api/payments")
    app.register_blueprint(user_bp, url_prefix="/api/users")

    return app
