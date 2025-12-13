from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.challenge import Challenge, UserChallenge, ChallengeProgress
from app.services.gemini_service import GeminiService
from datetime import datetime, date

bp = Blueprint('challenge', __name__, url_prefix='/api/challenges')
gemini = GeminiService()

# ============= GET ALL CHALLENGES (with user's join status) =============
@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_challenges():
    """Get all challenges with user's join status and progress"""
    try:
        user_id = get_jwt_identity()
        
        # Get all challenges
        challenges = Challenge.query.all()
        
        # Get user's joined challenges
        user_challenges = UserChallenge.query.filter_by(user_id=user_id).all()
        user_challenge_dict = {uc.challenge_id: uc for uc in user_challenges}
        
        result = []
        today = date.today()
        for challenge in challenges:
            user_challenge = user_challenge_dict.get(challenge.id)
            can_mark_today = True
            if user_challenge:
                # Check if progress already marked today
                today_progress = ChallengeProgress.query.filter_by(
                    user_challenge_id=user_challenge.id,
                    progress_date=today
                ).first()
                can_mark_today = today_progress is None and not user_challenge.is_completed
            
            result.append({
                'id': challenge.id,
                'title': challenge.title,
                'type': challenge.type,
                'duration': challenge.duration,
                'difficulty': challenge.difficulty,
                'goal': challenge.goal,
                'description': challenge.description,
                'is_ai_generated': challenge.is_ai_generated,
                'is_joined': user_challenge is not None,
                'progress': user_challenge.progress_percentage if user_challenge else 0,
                'is_completed': user_challenge.is_completed if user_challenge else False,
                'can_mark_today': can_mark_today,
                'created_at': challenge.created_at.isoformat()
            })
        
        return jsonify({'challenges': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= GENERATE AI CHALLENGES =============
@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_challenges():
    """Generate personalized challenges using Gemini AI"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prepare user data for AI
        user_data = {
            'age': request.json.get('age'),
            'gender': request.json.get('gender'),
            'weight': user.weight or request.json.get('weight'),
            'height': user.height or request.json.get('height'),
            'activity_level': request.json.get('activity_level'),
            'goal': request.json.get('goal')
        }
        
        # Generate challenges using Gemini
        ai_challenges = gemini.suggest_challenges(user_data)
        
        # Save challenges to database
        created_challenges = []
        for challenge_data in ai_challenges:
            challenge = Challenge(
                title=challenge_data.get('title'),
                type=challenge_data.get('type'),
                duration=challenge_data.get('duration'),
                difficulty=challenge_data.get('difficulty'),
                goal=challenge_data.get('goal'),
                description=challenge_data.get('description', ''),
                is_ai_generated=True
            )
            db.session.add(challenge)
            created_challenges.append({
                'title': challenge.title,
                'type': challenge.type,
                'duration': challenge.duration,
                'difficulty': challenge.difficulty,
                'goal': challenge.goal,
                'description': challenge.description
            })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Challenges generated successfully',
            'challenges': created_challenges
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= JOIN CHALLENGE =============
@bp.route('/<int:challenge_id>/join', methods=['POST'])
@jwt_required()
def join_challenge(challenge_id):
    """User joins a challenge"""
    try:
        user_id = get_jwt_identity()
        
        # Check if challenge exists
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        # Check if already joined
        existing = UserChallenge.query.filter_by(
            user_id=user_id,
            challenge_id=challenge_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Already joined this challenge'}), 400
        
        # Create user challenge
        user_challenge = UserChallenge(
            user_id=user_id,
            challenge_id=challenge_id,
            progress_percentage=0.0,
            is_completed=False
        )
        
        db.session.add(user_challenge)
        db.session.commit()
        
        return jsonify({
            'message': 'Challenge joined successfully',
            'user_challenge': {
                'id': user_challenge.id,
                'challenge_id': challenge_id,
                'progress': 0,
                'joined_at': user_challenge.joined_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= MARK PROGRESS (ONCE PER DAY) =============
@bp.route('/<int:challenge_id>/progress', methods=['POST'])
@jwt_required()
def mark_progress(challenge_id):
    """Mark progress for a challenge (only once per day)"""
    try:
        user_id = get_jwt_identity()
        today = date.today()
        
        # Get user challenge
        user_challenge = UserChallenge.query.filter_by(
            user_id=user_id,
            challenge_id=challenge_id
        ).first()
        
        if not user_challenge:
            return jsonify({'error': 'Challenge not joined'}), 404
        
        if user_challenge.is_completed:
            return jsonify({'error': 'Challenge already completed'}), 400
        
        # Check if already marked today
        existing_progress = ChallengeProgress.query.filter_by(
            user_challenge_id=user_challenge.id,
            progress_date=today
        ).first()
        
        if existing_progress:
            return jsonify({
                'error': 'Progress already marked for today',
                'already_marked': True
            }), 400
        
        # Calculate new progress (assuming each day is 10% for simplicity)
        # You can adjust this logic based on challenge duration
        duration_days = int(user_challenge.challenge.duration.split()[0]) if user_challenge.challenge.duration else 30
        progress_increment = 100.0 / duration_days
        
        new_progress = min(user_challenge.progress_percentage + progress_increment, 100.0)
        user_challenge.progress_percentage = new_progress
        
        # Mark as completed if progress reaches 100%
        if new_progress >= 100.0:
            user_challenge.is_completed = True
            user_challenge.completed_at = datetime.utcnow()
        
        # Create progress entry
        progress_entry = ChallengeProgress(
            user_challenge_id=user_challenge.id,
            progress_date=today
        )
        
        db.session.add(progress_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Progress marked successfully',
            'progress': new_progress,
            'is_completed': user_challenge.is_completed,
            'already_marked': False
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= GET USER'S CHALLENGES =============
@bp.route('/my-challenges', methods=['GET'])
@jwt_required()
def get_my_challenges():
    """Get all challenges joined by the current user"""
    try:
        user_id = get_jwt_identity()
        today = date.today()
        
        user_challenges = UserChallenge.query.filter_by(user_id=user_id).all()
        
        result = []
        for uc in user_challenges:
            # Check if progress marked today
            today_progress = ChallengeProgress.query.filter_by(
                user_challenge_id=uc.id,
                progress_date=today
            ).first()
            
            result.append({
                'id': uc.challenge.id,
                'title': uc.challenge.title,
                'type': uc.challenge.type,
                'duration': uc.challenge.duration,
                'difficulty': uc.challenge.difficulty,
                'goal': uc.challenge.goal,
                'description': uc.challenge.description,
                'progress': uc.progress_percentage,
                'is_completed': uc.is_completed,
                'can_mark_today': today_progress is None and not uc.is_completed,
                'joined_at': uc.joined_at.isoformat(),
                'completed_at': uc.completed_at.isoformat() if uc.completed_at else None
            })
        
        return jsonify({'challenges': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= GET CHALLENGE PROGRESS HISTORY =============
@bp.route('/<int:challenge_id>/history', methods=['GET'])
@jwt_required()
def get_progress_history(challenge_id):
    """Get progress history for a specific challenge"""
    try:
        user_id = get_jwt_identity()
        
        user_challenge = UserChallenge.query.filter_by(
            user_id=user_id,
            challenge_id=challenge_id
        ).first()
        
        if not user_challenge:
            return jsonify({'error': 'Challenge not joined'}), 404
        
        progress_entries = ChallengeProgress.query.filter_by(
            user_challenge_id=user_challenge.id
        ).order_by(ChallengeProgress.progress_date.desc()).all()
        
        return jsonify({
            'challenge_id': challenge_id,
            'progress_history': [{
                'date': entry.progress_date.isoformat(),
                'created_at': entry.created_at.isoformat()
            } for entry in progress_entries]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

