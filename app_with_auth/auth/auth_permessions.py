from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required


def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            identity_data = get_jwt_identity()
            user_roles = identity_data.get('roles', [])

            # Check if the user has any of the required roles
            if not any(role in user_roles for role in roles):
                return jsonify({"msg": "Access denied: insufficient role"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper
