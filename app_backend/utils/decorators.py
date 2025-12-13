import functools
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


def admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        from app.models.user import User

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user or user.role.role_name != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        return fn(*args, **kwargs)

    return wrapper


def auth_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


def role_required(roles):
    def wrapper(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            print(f"Role check is in progress for roles: {roles}")

            return f(*args, **kwargs)

        return decorated_function
    return wrapper
