from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.exercise_plan import ExercisePlan

bp_exercise = Blueprint('exercise', __name__, url_prefix='/api/exercise')


# ============= CREATE - GENERATE PLAN =============
@bp_exercise.route('/generate', methods=['POST'])
@jwt_required()
def generate_exercise_plan():
    """Generate personalized exercise plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate inputs
        required = ['weight', 'height', 'goal', 'difficulty_level']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Simple exercise plan generator based on inputs
        weight = int(data['weight'])
        height = int(data['height'])
        goal = data['goal']
        difficulty = data['difficulty_level']
        
        # Generate plan (you can make this more sophisticated)
        plan = generate_plan_logic(weight, height, goal, difficulty)
        
        exercise_plan = ExercisePlan(
            user_id=user_id,
            exercise_plan=plan,
            goal=goal,
            difficulty_level=difficulty,
            duration_weeks=int(data.get('duration_weeks', 4))
        )
        
        db.session.add(exercise_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Exercise plan generated',
            'plan': {
                'id': exercise_plan.id,
                'goal': exercise_plan.goal,
                'difficulty_level': exercise_plan.difficulty_level,
                'plan': exercise_plan.exercise_plan
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def generate_plan_logic(weight, height, goal, difficulty):
    """Generate exercise plan based on parameters"""
    
    exercises = {
        'beginner': [
            {'name': 'Push-ups', 'reps': '10-15', 'sets': 3},
            {'name': 'Squats', 'reps': '15-20', 'sets': 3},
            {'name': 'Plank', 'duration': '30 sec', 'sets': 3},
            {'name': 'Walking', 'duration': '20 min', 'sets': 1}
        ],
        'intermediate': [
            {'name': 'Push-ups', 'reps': '20-25', 'sets': 4},
            {'name': 'Squats', 'reps': '25-30', 'sets': 4},
            {'name': 'Burpees', 'reps': '10-15', 'sets': 3},
            {'name': 'Running', 'duration': '25 min', 'sets': 1}
        ],
        'advanced': [
            {'name': 'Push-ups', 'reps': '30-40', 'sets': 5},
            {'name': 'Jump Squats', 'reps': '20-25', 'sets': 4},
            {'name': 'Burpees', 'reps': '20-25', 'sets': 4},
            {'name': 'HIIT Training', 'duration': '30 min', 'sets': 1}
        ]
    }
    
    return {
        'goal': goal,
        'difficulty': difficulty,
        'bmi': round(weight / ((height/100) ** 2), 2),
        'weekly_schedule': exercises.get(difficulty, exercises['beginner'])
    }


# ============= READ (ALL) =============
@bp_exercise.route('/', methods=['GET'])
@jwt_required()
def get_exercise_plans():
    """Get all user exercise plans"""
    try:
        user_id = get_jwt_identity()
        
        plans = ExercisePlan.query.filter_by(user_id=user_id)\
            .order_by(ExercisePlan.created_at.desc()).all()
        
        return jsonify({
            'plans': [{
                'id': p.id,
                'goal': p.goal,
                'difficulty_level': p.difficulty_level,
                'duration_weeks': p.duration_weeks,
                'created_at': p.created_at.isoformat(),
                'plan': p.exercise_plan
            } for p in plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= READ (ONE) =============
@bp_exercise.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_exercise_plan(id):
    """Get specific exercise plan"""
    try:
        user_id = get_jwt_identity()
        plan = ExercisePlan.query.filter_by(id=id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        return jsonify({
            'id': plan.id,
            'goal': plan.goal,
            'difficulty_level': plan.difficulty_level,
            'duration_weeks': plan.duration_weeks,
            'created_at': plan.created_at.isoformat(),
            'plan': plan.exercise_plan
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= UPDATE =============
@bp_exercise.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_exercise_plan(id):
    """Update exercise plan"""
    try:
        user_id = get_jwt_identity()
        plan = ExercisePlan.query.filter_by(id=id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        data = request.get_json()
        
        if 'exercise_plan' in data:
            plan.exercise_plan = data['exercise_plan']
        if 'goal' in data:
            plan.goal = data['goal']
        if 'difficulty_level' in data:
            plan.difficulty_level = data['difficulty_level']
        if 'duration_weeks' in data:
            plan.duration_weeks = data['duration_weeks']
        
        db.session.commit()
        return jsonify({'message': 'Plan updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= DELETE =============
@bp_exercise.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_exercise_plan(id):
    """Delete exercise plan"""
    try:
        user_id = get_jwt_identity()
        plan = ExercisePlan.query.filter_by(id=id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        db.session.delete(plan)
        db.session.commit()
        return jsonify({'message': 'Plan deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500