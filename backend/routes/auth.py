from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
import os
from datetime import datetime
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
client = MongoClient(mongo_uri)
db = client.get_database()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if db.users.find_one({"email": data["email"]}):
        return jsonify({"msg": "Email already registered."}), 400
    user = {
        "name": data["name"],
        "email": data["email"],
        "password_hash": generate_password_hash(data["password"]),
        #"brain_type": data.get("brain_type"),
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user)
    return jsonify({"msg": "User registered successfully."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = db.users.find_one({"email": data["email"]})
    if not user or not check_password_hash(user["password_hash"], data["password"]):
        return jsonify({"msg": "Invalid credentials."}), 401
    access_token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": access_token}), 200

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"msg": "Invalid token."}), 401
    
    user_data = {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user["email"],
        "brain_type": user.get("brain_type")
    }
    
    return jsonify({
        "msg": "Token valid.", 
        "user": user_data
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get("email")

    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"msg": "User not found"}), 404

    import secrets
    token = secrets.token_urlsafe(32)

    db.users.update_one(
        {"email": email},
        {"$set": {
            "reset_token": token,
            "reset_token_created_at": datetime.utcnow()
        }}
    )

    # In real app → send email
    return jsonify({
        "msg": "Reset token generated",
        "reset_token": token   # remove this in production
    }), 200
    
    
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get("token")
    new_password = data.get("new_password")

    user = db.users.find_one({"reset_token": token})
    if not user:
        return jsonify({"msg": "Invalid or expired token"}), 400

    # OPTIONAL: Token expiry check (15 min)
    from datetime import timedelta
    if datetime.utcnow() - user.get("reset_token_created_at", datetime.utcnow()) > timedelta(minutes=15):
        return jsonify({"msg": "Token expired"}), 400

    hashed_password = generate_password_hash(new_password)

    db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password_hash": hashed_password},
            "$unset": {
                "reset_token": "",
                "reset_token_created_at": ""
            }
        }
    )

    return jsonify({"msg": "Password reset successful"}), 200