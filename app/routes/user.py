import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.user import UserHelper
import uuid

user_bp = Blueprint("user", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

@user_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"success": True, "message": "User API is online 🚀"}), 200

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = UserHelper.get_by_id(user_id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        return jsonify({"success": True, "user": user}), 200
    except Exception as e:
        print(f"PROFILE FETCH ERROR: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()

    updated_user = UserHelper.update_user(user_id, data)
    return jsonify({"success": True, "message": "Profile updated", "user": updated_user}), 200

@user_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add uuid to prevent collisions
        filename = f"{uuid.uuid4()}_{filename}"

        upload_path = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file.save(os.path.join(upload_path, filename))

        # In a real cloud environment, this would be the URL of the uploaded file
        # Here we'll return the relative path that the backend can serve
        file_url = f"{request.host_url}api/users/uploads/{filename}"

        return jsonify({"success": True, "file_url": file_url}), 200

    return jsonify({"success": False, "message": "File type not allowed"}), 400

@user_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
