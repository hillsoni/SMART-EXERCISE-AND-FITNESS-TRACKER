from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.yoga import Yoga
from app.models.user import User
from app.services.minio_service import MinioService

from app.utils.decorators import admin_required

bp = Blueprint('yoga', __name__, url_prefix='/api/yoga')
minio = MinioService()

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============= CREATE =============
@bp.route('/', methods=['POST'])
@admin_required
def create_yoga():
    """Create new yoga pose (Admin only)"""
    try:
        # Check if multipart form
        if 'photo' not in request.files:
            return jsonify({'error': 'Photo is required'}), 400

        photo = request.files['photo']

        if photo.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(photo.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400

        # Get form data
        yoga_name = request.form.get('yoga_name')
        yoga_description = request.form.get('yoga_description')
        difficulty_level = request.form.get('difficulty_level', 'beginner')
        duration_minutes = request.form.get('duration_minutes', type=int)
        benefits = request.form.get('benefits')

        if not yoga_name:
            return jsonify({'error': 'Yoga name is required'}), 400

        # Upload image to MinIO
        photo_url = minio.upload_file(photo, folder='yoga')

        # Create yoga entry
        yoga = Yoga(
            yoga_name=yoga_name,
            yoga_description=yoga_description,
            photo_url=photo_url,
            difficulty_level=difficulty_level,
            duration_minutes=duration_minutes,
            benefits=benefits
        )

        db.session.add(yoga)
        db.session.commit()

        return jsonify({
            'message': 'Yoga pose created successfully',
            'yoga': {
                'id': yoga.id,
                'yoga_name': yoga.yoga_name,
                'yoga_description': yoga.yoga_description,
                'photo_url': yoga.photo_url,
                'difficulty_level': yoga.difficulty_level,
                'duration_minutes': yoga.duration_minutes,
                'benefits': yoga.benefits
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= READ (ALL) =============
@bp.route('/', methods=['GET'])
def get_all_yoga():
    """Get all yoga poses with filters"""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Filters
        difficulty_level = request.args.get('difficulty_level')
        search = request.args.get('search')

        query = Yoga.query

        if difficulty_level:
            query = query.filter_by(difficulty_level=difficulty_level)

        if search:
            query = query.filter(
                db.or_(
                    Yoga.yoga_name.ilike(f'%{search}%'),
                    Yoga.yoga_description.ilike(f'%{search}%')
                )
            )

        yoga_poses = query.order_by(Yoga.yoga_name)\
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'yoga_poses': [{
                'id': yoga.id,
                'yoga_name': yoga.yoga_name,
                'yoga_description': yoga.yoga_description,
                'photo_url': yoga.photo_url,
                'difficulty_level': yoga.difficulty_level,
                'duration_minutes': yoga.duration_minutes,
                'benefits': yoga.benefits
            } for yoga in yoga_poses.items],
            'total': yoga_poses.total,
            'page': yoga_poses.page,
            'pages': yoga_poses.pages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= READ (ONE) =============
@bp.route('/<int:id>', methods=['GET'])
def get_yoga(id):
    """Get specific yoga pose by ID"""
    try:
        yoga = Yoga.query.get(id)

        if not yoga:
            return jsonify({'error': 'Yoga pose not found'}), 404

        return jsonify({
            'id': yoga.id,
            'yoga_name': yoga.yoga_name,
            'yoga_description': yoga.yoga_description,
            'photo_url': yoga.photo_url,
            'difficulty_level': yoga.difficulty_level,
            'duration_minutes': yoga.duration_minutes,
            'benefits': yoga.benefits
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= UPDATE =============
@bp.route('/<int:id>', methods=['PUT'])
@admin_required
def update_yoga(id):
    """Update yoga pose (Admin only)"""
    try:
        yoga = Yoga.query.get(id)

        if not yoga:
            return jsonify({'error': 'Yoga pose not found'}), 404

        # Check if there's a new photo
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '' and allowed_file(photo.filename):
                # Delete old photo
                if yoga.photo_url:
                    try:
                        old_path = yoga.photo_url.split('/')[-1]
                        minio.delete_file(f'yoga/{old_path}')
                    except:
                        pass

                # Upload new photo
                yoga.photo_url = minio.upload_file(photo, folder='yoga')

        # Update other fields
        if 'yoga_name' in request.form:
            yoga.yoga_name = request.form['yoga_name']

        if 'yoga_description' in request.form:
            yoga.yoga_description = request.form['yoga_description']

        if 'difficulty_level' in request.form:
            yoga.difficulty_level = request.form['difficulty_level']

        if 'duration_minutes' in request.form:
            yoga.duration_minutes = int(request.form['duration_minutes'])

        if 'benefits' in request.form:
            yoga.benefits = request.form['benefits']

        db.session.commit()

        return jsonify({
            'message': 'Yoga pose updated successfully',
            'yoga': {
                'id': yoga.id,
                'yoga_name': yoga.yoga_name,
                'yoga_description': yoga.yoga_description,
                'photo_url': yoga.photo_url,
                'difficulty_level': yoga.difficulty_level,
                'duration_minutes': yoga.duration_minutes,
                'benefits': yoga.benefits
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= DELETE =============
@bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_yoga(id):
    """Delete yoga pose (Admin only)"""
    try:
        yoga = Yoga.query.get(id)

        if not yoga:
            return jsonify({'error': 'Yoga pose not found'}), 404

        # Delete photo from MinIO
        if yoga.photo_url:
            try:
                photo_path = yoga.photo_url.split('/')[-1]
                minio.delete_file(f'yoga/{photo_path}')
            except:
                pass

        db.session.delete(yoga)
        db.session.commit()

        return jsonify({'message': 'Yoga pose deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= ADDITIONAL - GET BY DIFFICULTY =============
@bp.route('/difficulty/<level>', methods=['GET'])
def get_yoga_by_difficulty(level):
    """Get yoga poses by difficulty level"""
    try:
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if level not in valid_levels:
            return jsonify({'error': 'Invalid difficulty level'}), 400

        yoga_poses = Yoga.query.filter_by(difficulty_level=level).all()

        return jsonify({
            'difficulty_level': level,
            'count': len(yoga_poses),
            'yoga_poses': [{
                'id': yoga.id,
                'yoga_name': yoga.yoga_name,
                'yoga_description': yoga.yoga_description,
                'photo_url': yoga.photo_url,
                'duration_minutes': yoga.duration_minutes,
                'benefits': yoga.benefits
            } for yoga in yoga_poses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
