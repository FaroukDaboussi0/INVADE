from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

def check_ip_and_user_agent(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Retrieve JWT identity
        identity = get_jwt_identity()

        # Extract expected IP and user agent from JWT identity
        token_ip_address = identity.get('ip_address')
        token_user_agent = identity.get('user_agent')

        # Extract actual IP and user agent from request
        request_ip_address = request.remote_addr
        request_user_agent = request.headers.get('User-Agent')

        # Check if IP and user agent match
        if token_ip_address != request_ip_address or token_user_agent != request_user_agent:
            return jsonify({'msg': 'must reconnect' , "agent" : request_user_agent}), 401

        return func(*args, **kwargs)
    return decorated_function