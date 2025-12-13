from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.workout import Workout
from app.models.user import User
from app.services.minio_service import MinioService

from app.utils.decorators import admin_required

bp = Blueprint('workout', __name__, url_prefix='/api/workouts')
minio = MinioService()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============= CREATE =============
@bp.route('/', methods=['POST'])
@admin_required
def create_workout():
    """Create new workout (Admin only)"""
    try:
        # Handle optional photo
        photo_url = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '' and allowed_file(photo.filename):
                photo_url = minio.upload_file(photo, folder='workouts')

        workout = Workout(
            workout_name=request.form.get('workout_name'),
            workout_description=request.form.get('workout_description'),
            category=request.form.get('category', 'strength'),
            difficulty_level=request.form.get('difficulty_level', 'beginner'),
            duration_minutes=int(request.form.get('duration_minutes', 0)),
            calories_burned=int(request.form.get('calories_burned', 0)),
            equipment_needed=request.form.get('equipment_needed'),
            photo_url=photo_url
        )

        db.session.add(workout)
        db.session.commit()

        return jsonify({
            'message': 'Workout created successfully',
            'workout': {
                'id': workout.id,
                'workout_name': workout.workout_name,
                'category': workout.category,
                'difficulty_level': workout.difficulty_level
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= READ (ALL) =============
@bp.route('/', methods=['GET'])
def get_all_workouts():
    """Get all workouts with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        search = request.args.get('search')

        query = Workout.query

        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        if search:
            query = query.filter(
                db.or_(
                    Workout.workout_name.ilike(f'%{search}%'),
                    Workout.workout_description.ilike(f'%{search}%')
                )
            )

        workouts = query.order_by(Workout.workout_name)\
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'workouts': [{
                'id': w.id,
                'workout_name': w.workout_name,
                'workout_description': w.workout_description,
                'category': w.category,
                'difficulty_level': w.difficulty_level,
                'duration_minutes': w.duration_minutes,
                'calories_burned': w.calories_burned,
                'equipment_needed': w.equipment_needed,
                'photo_url': w.photo_url
            } for w in workouts.items],
            'total': workouts.total,
            'page': workouts.page,
            'pages': workouts.pages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= READ (ONE) =============
@bp.route('/<int:id>', methods=['GET'])
def get_workout(id):
    """Get specific workout"""
    try:
        workout = Workout.query.get(id)
        if not workout:
            return jsonify({'error': 'Workout not found'}), 404

        return jsonify({
            'id': workout.id,
            'workout_name': workout.workout_name,
            'workout_description': workout.workout_description,
            'category': workout.category,
            'difficulty_level': workout.difficulty_level,
            'duration_minutes': workout.duration_minutes,
            'calories_burned': workout.calories_burned,
            'equipment_needed': workout.equipment_needed,
            'photo_url': workout.photo_url
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= UPDATE =============
@bp.route('/<int:id>', methods=['PUT'])
@admin_required
def update_workout(id):
    """Update workout"""
    try:
        workout = Workout.query.get(id)
        if not workout:
            return jsonify({'error': 'Workout not found'}), 404

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '' and allowed_file(photo.filename):
                if workout.photo_url:
                    try:
                        old_path = workout.photo_url.split('/')[-1]
                        minio.delete_file(f'workouts/{old_path}')
                    except:
                        pass
                workout.photo_url = minio.upload_file(photo, folder='workouts')

        # Update fields
        for field in ['workout_name', 'workout_description', 'category',
                      'difficulty_level', 'equipment_needed']:
            if field in request.form:
                setattr(workout, field, request.form[field])

        if 'duration_minutes' in request.form:
            workout.duration_minutes = int(request.form['duration_minutes'])
        if 'calories_burned' in request.form:
            workout.calories_burned = int(request.form['calories_burned'])

        db.session.commit()
        return jsonify({'message': 'Workout updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= DELETE =============
@bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_workout(id):
    """Delete workout"""
    try:
        workout = Workout.query.get(id)
        if not workout:
            return jsonify({'error': 'Workout not found'}), 404

        if workout.photo_url:
            try:
                photo_path = workout.photo_url.split('/')[-1]
                minio.delete_file(f'workouts/{photo_path}')
            except:
                pass

        db.session.delete(workout)
        db.session.commit()
        return jsonify({'message': 'Workout deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
