from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.diet_plan import DietPlan
from app.models.exercise_plan import ExercisePlan
from app.models.chatbot_query import ChatbotQuery

from app.utils.decorators import admin_required

bp_user = Blueprint('user', __name__, url_prefix='/api/users')

# ============= READ (ALL) - Admin Only =============
@bp_user.route('/', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (Admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        users = User.query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'mobile_number': u.mobile_number,
                'height': u.height,
                'weight': u.weight,
                'role': u.role.role_name,
                'created_at': u.created_at.isoformat()
            } for u in users.items],
            'total': users.total,
            'page': users.page,
            'pages': users.pages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= READ (ONE) =============
@bp_user.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """Get user by ID"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        # Users can only view their own profile, admins can view anyone
        if current_user_id != id and current_user.role.role_name != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'mobile_number': user.mobile_number,
            'height': user.height,
            'weight': user.weight,
            'role': user.role.role_name,
            'created_at': user.created_at.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= UPDATE =============
@bp_user.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """Update user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only update their own profile, admins can update anyone
        if current_user_id != id and current_user.role.role_name != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'username' in data:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != id:
                return jsonify({'error': 'Username already taken'}), 409
            user.username = data['username']

        if 'mobile_number' in data:
            user.mobile_number = data['mobile_number']

        if 'height' in data:
            user.height = float(data['height']) if data['height'] else None

        if 'weight' in data:
            user.weight = float(data['weight']) if data['weight'] else None

        if 'password' in data:
            user.set_password(data['password'])

        # Only admin can change roles
        if 'role_id' in data and current_user.role.role_name == 'admin':
            user.role_id = data['role_id']

        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= DELETE =============
@bp_user.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    """Delete user (Admin only)"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Prevent deleting last admin
        if user.role.role_name == 'admin':
            admin_count = User.query.join(User.role).filter_by(role_name='admin').count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete last admin'}), 400

        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= GET USER STATISTICS =============
@bp_user.route('/<int:id>/stats', methods=['GET'])
@jwt_required()
def get_user_stats(id):
    """Get user statistics"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only view their own stats, admins can view anyone
        if current_user_id != id and current_user.role.role_name != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Count related records
        diet_plans_count = DietPlan.query.filter_by(user_id=id).count()
        exercise_plans_count = ExercisePlan.query.filter_by(user_id=id).count()
        chatbot_queries_count = ChatbotQuery.query.filter_by(user_id=id).count()

        # Latest activity
        latest_diet = DietPlan.query.filter_by(user_id=id)\
            .order_by(DietPlan.created_at.desc()).first()
        latest_exercise = ExercisePlan.query.filter_by(user_id=id)\
            .order_by(ExercisePlan.created_at.desc()).first()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'joined': user.created_at.isoformat()
            },
            'statistics': {
                'total_diet_plans': diet_plans_count,
                'total_exercise_plans': exercise_plans_count,
                'total_chatbot_queries': chatbot_queries_count
            },
            'latest_activity': {
                'diet_plan': {
                    'id': latest_diet.id,
                    'goal': latest_diet.goal,
                    'created_at': latest_diet.created_at.isoformat()
                } if latest_diet else None,
                'exercise_plan': {
                    'id': latest_exercise.id,
                    'goal': latest_exercise.goal,
                    'created_at': latest_exercise.created_at.isoformat()
                } if latest_exercise else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= SEARCH USERS =============
@bp_user.route('/search', methods=['GET'])
@admin_required
def search_users():
    """Search users by username or email (Admin only)"""
    try:
        query_param = request.args.get('q', '').strip()

        if not query_param:
            return jsonify({'error': 'Search query required'}), 400

        users = User.query.filter(
            db.or_(
                User.username.ilike(f'%{query_param}%'),
                User.email.ilike(f'%{query_param}%')
            )
        ).limit(20).all()

        return jsonify({
            'results': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role.role_name
            } for u in users]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
