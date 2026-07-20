from flask import jsonify


def success(message, data=None, status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status_code


def error(message, status_code=400):
    return jsonify({
        "success": False,
        "message": message
    }), status_code