# app/routes/chatbot.py - Chatbot with Gemini AI

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.chatbot_query import ChatbotQuery
from app.services.gemini_service import GeminiService
from datetime import datetime, timedelta

bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')
gemini = GeminiService()

# ============= CREATE - SEND QUERY =============
@bp.route('/query', methods=['POST'])
@jwt_required()
def send_query():
    """Send question to chatbot and get AI response"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('question'):
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question'].strip()
        query_type = data.get('query_type', 'diet')  # Default to diet
        
        # Validate query type - only diet allowed
        if query_type != 'diet':
            return jsonify({
                'error': 'Only diet-related queries are supported',
                'message': 'Please ask questions about nutrition, meal planning, or dietary advice'
            }), 400
        
        # Check for diet-related keywords
        diet_keywords = ['diet', 'food', 'meal', 'nutrition', 'calorie', 'protein', 
                        'carb', 'fat', 'vitamin', 'eat', 'recipe', 'ingredient']
        
        if not any(keyword in question.lower() for keyword in diet_keywords):
            return jsonify({
                'error': 'Question must be diet-related',
                'message': 'I can only answer questions about diet and nutrition'
            }), 400
        
        # Generate response using Gemini
        ai_answer = gemini.chat_response(question, context='diet')
        
        # Save to database
        query = ChatbotQuery(
            user_id=user_id,
            question=question,
            answer=ai_answer,
            query_type=query_type
        )
        
        db.session.add(query)
        db.session.commit()
        
        return jsonify({
            'id': query.id,
            'question': query.question,
            'answer': query.answer,
            'query_type': query.query_type,
            'created_at': query.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= READ - GET CHAT HISTORY =============
@bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    """Get user's chat history"""
    try:
        user_id = get_jwt_identity()
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filter by query type
        query_type = request.args.get('query_type', 'diet')
        
        # Filter by date range
        days = request.args.get('days', type=int)
        
        query = ChatbotQuery.query.filter_by(user_id=user_id, query_type=query_type)
        
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ChatbotQuery.created_at >= start_date)
        
        queries = query.order_by(ChatbotQuery.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'queries': [{
                'id': q.id,
                'question': q.question,
                'answer': q.answer,
                'query_type': q.query_type,
                'created_at': q.created_at.isoformat()
            } for q in queries.items],
            'total': queries.total,
            'page': queries.page,
            'pages': queries.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= READ - GET SPECIFIC QUERY =============
@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_query(id):
    """Get specific query by ID"""
    try:
        user_id = get_jwt_identity()
        
        query = ChatbotQuery.query.filter_by(id=id, user_id=user_id).first()
        
        if not query:
            return jsonify({'error': 'Query not found'}), 404
        
        return jsonify({
            'id': query.id,
            'question': query.question,
            'answer': query.answer,
            'query_type': query.query_type,
            'created_at': query.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= DELETE - DELETE QUERY =============
@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_query(id):
    """Delete specific query"""
    try:
        user_id = get_jwt_identity()
        
        query = ChatbotQuery.query.filter_by(id=id, user_id=user_id).first()
        
        if not query:
            return jsonify({'error': 'Query not found'}), 404
        
        db.session.delete(query)
        db.session.commit()
        
        return jsonify({'message': 'Query deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= DELETE - CLEAR HISTORY =============
@bp.route('/history', methods=['DELETE'])
@jwt_required()
def clear_history():
    """Clear all chat history for user"""
    try:
        user_id = get_jwt_identity()
        
        # Optional: only clear specific query type
        query_type = request.args.get('query_type')
        
        if query_type:
            ChatbotQuery.query.filter_by(user_id=user_id, query_type=query_type).delete()
        else:
            ChatbotQuery.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({'message': 'Chat history cleared successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= ADDITIONAL - GET STATISTICS =============
@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get chat statistics"""
    try:
        user_id = get_jwt_identity()
        
        total_queries = ChatbotQuery.query.filter_by(user_id=user_id).count()
        
        # Queries by type
        queries_by_type = db.session.query(
            ChatbotQuery.query_type,
            db.func.count(ChatbotQuery.id)
        ).filter_by(user_id=user_id).group_by(ChatbotQuery.query_type).all()
        
        # Recent activity
        today = datetime.utcnow().date()
        today_queries = ChatbotQuery.query.filter_by(user_id=user_id)\
            .filter(db.func.date(ChatbotQuery.created_at) == today).count()
        
        # Most recent query
        latest_query = ChatbotQuery.query.filter_by(user_id=user_id)\
            .order_by(ChatbotQuery.created_at.desc()).first()
        
        return jsonify({
            'total_queries': total_queries,
            'queries_by_type': {qtype: count for qtype, count in queries_by_type},
            'today_queries': today_queries,
            'latest_query': {
                'id': latest_query.id,
                'question': latest_query.question[:50] + '...' if len(latest_query.question) > 50 else latest_query.question,
                'created_at': latest_query.created_at.isoformat()
            } if latest_query else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= ADDITIONAL - QUICK ASK =============
@bp.route('/quick-ask', methods=['POST'])
@jwt_required()
def quick_ask():
    """Quick ask without saving to database"""
    try:
        data = request.get_json()
        
        if not data.get('question'):
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question'].strip()
        
        # Generate response
        answer = gemini.chat_response(question, context='diet')
        
        return jsonify({
            'question': question,
            'answer': answer,
            'saved': False
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500