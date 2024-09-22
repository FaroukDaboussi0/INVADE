from datetime import timedelta
from functools import wraps
from flask import Blueprint, app,current_app, g, make_response,  request, jsonify
from flask_mail import  Message
import jwt

from Models.Roles import RoleEnum
from Models.Users import User
from auth.auth_ip_agent_verif_middleware import check_ip_and_user_agent

from auth.auth_permessions import roles_required
from auth.auth_schemas import RegistrationSchema, LoginSchema
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token , create_refresh_token , get_jwt_identity, jwt_required, set_access_cookies, set_refresh_cookies, verify_jwt_in_request
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp 
from flask_login import login_user



@auth_bp.route('/register', methods=['POST'])
def register():
    schema = RegistrationSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    username = data['username']
    email = data['email']
    password = data['password']

    if User.objects(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_verified=False  # Initially, the account is not verified
    )
    user.save()

    # Send verification email
    send_verification_email(user)

    return jsonify({"message": "User registered successfully. Please check your email to verify your account."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.objects(email=email).first()

    if user and user.verify_password(password):
        if not user.is_verified:
            return jsonify({"error": "Account not verified. Please check your email."}), 400
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        identity = {
            'user_id': str(user.id),
            'roles': user.roles,
            'ip_address': ip_address,
            'user_agent': user_agent
        }

        print(identity)
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        response = make_response(jsonify({'msg': 'Login successful'}))
        response.headers['Authorization'] = f'Bearer {access_token}'
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Lax')
        login_user(user)
        return response

    return jsonify({"error": "Invalid email or password."}), 401

def send_verification_email(user):
    mail = current_app.extensions.get('mail')
    # Generate a JWT token with a short expiration time (e.g., 1 hour)
    token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))

    # Build the verification link
    base_url = current_app.config['BASE_URL']
    verification_link = f"{base_url}/auth/verify_account/{token}"

    # Compose the email
    subject = "Email Verification"
    recipients = [user.email]
    sender = current_app.config['MAIL_USERNAME']
    body = f"Hello {user.username},\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nIf you did not sign up for this account, please ignore this email."

    # Create the message
    msg = Message(subject=subject, recipients=recipients, sender=sender, body=body)

    # Send the email
    try:
        mail.send(msg)
        print(f"Verification email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email to {user.email}. Error: {str(e)}")


@auth_bp.route('/verify_account/<token>', methods=['GET'])
def verify_account(token):
    try:
        # Decode the token to get the user ID
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']  # 'sub' contains the user's identity, which is the user ID
      
    except Exception as e:
        return jsonify({"error": "Invalid or expired verification token."}), 400

    # Find the user by ID and verify their account
    try:
        user = User.objects.get(id=user_id)
        if user.is_verified:
          return jsonify({"message": "Account is already verified"}), 400
        user.is_verified = True
        user.save()
        return jsonify({"message": "Email verified successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"User not found."}), 404
    
@auth_bp.route('/resend_verification_email', methods=['POST'])
def resend_verification_email():
    # Get email from the request
    email = request.json.get('email')

    if not email:
        return jsonify({"message": "Email is required"}), 400

    # Check if the user exists
    user = User.objects(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check if the account is already verified
    if user.is_verified:
        return jsonify({"message": "Account is already verified"}), 400

    # If user exists and not verified, resend the verification email
    send_verification_email(user)
    return jsonify({"message": "Verification email has been resent"}), 200

@auth_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    new_password = request.json.get('password')
    
    if not new_password:
        return jsonify({"message": "New password is required"}), 400
    
    try:
        # Decode the token to get the user ID
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
        
        # Find the user by ID
        user = User.objects.get(id=user_id)
        user.password = new_password
        user.save()
        
        return jsonify({"message": "Password has been reset successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Invalid or expired token"}), 400
    
@auth_bp.route('/forget_password', methods=['POST'])
def forget_password():
    email = request.json.get('email')
    
    if not email:
        return jsonify({"message": "Email is required"}), 400
    
    user = User.objects(email=email).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if user.is_verified:
        # Generate a JWT token with a short expiration time
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
        
        # Send password reset email
        send_password_reset_email(user, token)
        
        return jsonify({"message": "Password reset email has been sent"}), 200
    else:
        return jsonify({"message": "Account not verified"}), 400

def send_password_reset_email(user, token):
    mail = current_app.extensions.get('mail')
    base_url = current_app.config['BASE_URL']
    reset_link = f"{base_url}/auth/reset_password/{token}"
    message = f"Please reset your password by clicking the link: {reset_link}"
    
    msg = Message("Password Reset Request", sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = message
    
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

@auth_bp.route('/token/refresh', methods=['POST'])
def refresh_token():
    # Extract the refresh token from cookies
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        return jsonify({'msg': 'Refresh token is missing'}), 401

    try:
        # Decode and verify the refresh token
        decoded_refresh_token = decode_token(refresh_token)
        
        # Extract user identity and stored IP and user agent
        user_identity = decoded_refresh_token['sub']  # Get the user identity (e.g., user ID)
        stored_ip = decoded_refresh_token.get('ip')
        stored_user_agent = decoded_refresh_token.get('user_agent')

        # Get current IP and user agent
        current_ip = request.remote_addr
        current_user_agent = request.headers.get('User-Agent')

        # Verify if the current IP and user agent match the stored ones
        if stored_ip != current_ip or stored_user_agent != current_user_agent:
            return jsonify({'msg': 'Token is not valid for this IP or user agent'}), 401

        # Generate new tokens
        access_token = create_access_token(identity=user_identity)
        new_refresh_token = create_refresh_token(identity=user_identity, additional_claims={
            'ip': current_ip,
            'user_agent': current_user_agent
        })

        # Set new tokens in cookies
        response = make_response(jsonify({'msg': 'Tokens refreshed'}))
        response.headers['Authorization'] = f'Bearer {access_token}'
        response.set_cookie(
            'refresh_token', 
            new_refresh_token, 
            httponly=True, 
            secure=True, 
            samesite='Lax'
        )

        return response
    except jwt.ExpiredSignatureError:
        return jsonify({'msg': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'msg': 'Invalid refresh token'}), 401

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
@check_ip_and_user_agent
@roles_required(RoleEnum.USER.value)
def protected():
    # Access the user info stored in g
    current_user = get_jwt_identity()
    if current_user:
        return jsonify({'user': current_user})
    return jsonify({'msg': 'User information not found'}), 401