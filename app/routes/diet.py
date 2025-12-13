# app/routes/diet.py - Complete CRUD Example

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.diet_plan import DietPlan
from app.services.gemini_service import GeminiService

bp = Blueprint('diet', __name__, url_prefix='/api/diet')
gemini = GeminiService()

# ============= CREATE =============
@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_diet_plan():
    """Generate personalized diet plan using Gemini AI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['age', 'gender', 'weight', 'height', 'activity_level', 'goal', 'diet_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate diet plan using Gemini
        ai_response = gemini.generate_diet_plan(data)
        
        # Create diet plan object
        diet_plan = DietPlan(
            user_id=user_id,
            diet_plan={
                'user_info': data,
                'meal_plan': ai_response,
                'generated_by': 'gemini-ai'
            },
            goal=data.get('goal'),
            diet_type=data.get('diet_type'),
            duration=data.get('duration', '1_month')
        )
        
        db.session.add(diet_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Diet plan generated successfully',
            'diet_plan': {
                'id': diet_plan.id,
                'plan': diet_plan.diet_plan,
                'created_at': diet_plan.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= READ (ALL) =============
@bp.route('/', methods=['GET'])
@jwt_required()
def get_user_diet_plans():
    """Get all diet plans for current user"""
    try:
        user_id = get_jwt_identity()
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        diet_plans = DietPlan.query.filter_by(user_id=user_id)\
            .order_by(DietPlan.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'diet_plans': [{
                'id': plan.id,
                'goal': plan.goal,
                'diet_type': plan.diet_type,
                'duration': plan.duration,
                'created_at': plan.created_at.isoformat(),
                'plan': plan.diet_plan
            } for plan in diet_plans.items],
            'total': diet_plans.total,
            'page': diet_plans.page,
            'pages': diet_plans.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= READ (ONE) =============
@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_diet_plan(id):
    """Get specific diet plan by ID"""
    try:
        user_id = get_jwt_identity()
        
        diet_plan = DietPlan.query.filter_by(id=id, user_id=user_id).first()
        
        if not diet_plan:
            return jsonify({'error': 'Diet plan not found'}), 404
        
        return jsonify({
            'id': diet_plan.id,
            'goal': diet_plan.goal,
            'diet_type': diet_plan.diet_type,
            'duration': diet_plan.duration,
            'created_at': diet_plan.created_at.isoformat(),
            'plan': diet_plan.diet_plan
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= UPDATE =============
@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_diet_plan(id):
    """Update existing diet plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        diet_plan = DietPlan.query.filter_by(id=id, user_id=user_id).first()
        
        if not diet_plan:
            return jsonify({'error': 'Diet plan not found'}), 404
        
        # Update fields
        if 'goal' in data:
            diet_plan.goal = data['goal']
        if 'diet_type' in data:
            diet_plan.diet_type = data['diet_type']
        if 'duration' in data:
            diet_plan.duration = data['duration']
        if 'diet_plan' in data:
            diet_plan.diet_plan = data['diet_plan']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Diet plan updated successfully',
            'diet_plan': {
                'id': diet_plan.id,
                'goal': diet_plan.goal,
                'diet_type': diet_plan.diet_type,
                'plan': diet_plan.diet_plan
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= DELETE =============
@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_diet_plan(id):
    """Delete diet plan"""
    try:
        user_id = get_jwt_identity()
        
        diet_plan = DietPlan.query.filter_by(id=id, user_id=user_id).first()
        
        if not diet_plan:
            return jsonify({'error': 'Diet plan not found'}), 404
        
        db.session.delete(diet_plan)
        db.session.commit()
        
        return jsonify({'message': 'Diet plan deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= ADDITIONAL USEFUL ENDPOINTS =============

@bp.route('/latest', methods=['GET'])
@jwt_required()
def get_latest_diet_plan():
    """Get user's most recent diet plan"""
    try:
        user_id = get_jwt_identity()
        
        diet_plan = DietPlan.query.filter_by(user_id=user_id)\
            .order_by(DietPlan.created_at.desc())\
            .first()
        
        if not diet_plan:
            return jsonify({'message': 'No diet plans found'}), 404
        
        return jsonify({
            'id': diet_plan.id,
            'goal': diet_plan.goal,
            'diet_type': diet_plan.diet_type,
            'duration': diet_plan.duration,
            'created_at': diet_plan.created_at.isoformat(),
            'plan': diet_plan.diet_plan
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/latest', methods=['GET'])
@jwt_required()
def get_latest_diet():
    user_id = get_jwt_identity()
    latest_diet = DietPlan.query.filter_by(user_id=user_id)\
        .order_by(DietPlan.created_at.desc()).first()
    
    if not latest_diet:
        return jsonify({'diet_plan': None}), 200
    
    return jsonify({
        'diet_plan': {
            'id': latest_diet.id,
            'goal': latest_diet.goal,
            'diet_type': latest_diet.diet_type,
            'duration': latest_diet.duration,
            'created_at': latest_diet.created_at.isoformat()
        }
    }), 200
@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_diet_statistics():
    """Get statistics about user's diet plans"""
    try:
        user_id = get_jwt_identity()
        
        total_plans = DietPlan.query.filter_by(user_id=user_id).count()
        
        goals_count = db.session.query(
            DietPlan.goal, 
            db.func.count(DietPlan.goal)
        ).filter_by(user_id=user_id).group_by(DietPlan.goal).all()
        
        diet_types_count = db.session.query(
            DietPlan.diet_type,
            db.func.count(DietPlan.diet_type)
        ).filter_by(user_id=user_id).group_by(DietPlan.diet_type).all()
        
        return jsonify({
            'total_plans': total_plans,
            'goals': {goal: count for goal, count in goals_count},
            'diet_types': {dtype: count for dtype, count in diet_types_count}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500