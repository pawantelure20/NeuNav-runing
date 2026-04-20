from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from pymongo import MongoClient
import os
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
client = MongoClient(mongo_uri)
db = client.get_database()

@quiz_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    """Get all quiz questions"""
    try:
        questions = list(db.quiz_questions.find())
        formatted_questions = []
        
        for i, q in enumerate(questions):
            formatted_q = {
                'question_id': f"q{i + 1}",  # Use clean question IDs like "q1", "q2", etc.
                'question_number': i + 1,
                'text': q['text'],
                'options': []
            }
            
            # Format options with option_id
            for j, option in enumerate(q.get('options', [])):
                formatted_option = {
                    'option_id': j + 1,
                    'text': option.get('text', ''),
                    'brain_type': option.get('brain_type', '')
                }
                formatted_q['options'].append(formatted_option)
            
            formatted_questions.append(formatted_q)
        
        return jsonify({
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'instructions': 'Choose the option that best describes your learning preferences.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    """Submit quiz answers and generate roadmap"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'answers' not in data:
            return jsonify({'error': 'Answers are required'}), 400
        
        answers = data['answers']
        preferences = data.get('preferences', {})
        
        # Calculate brain type from answers
        brain_type_counts = {'Visual': 0, 'Auditory': 0, 'ReadWrite': 0, 'Kinesthetic': 0}
        
        # Get questions to map answers to brain types
        questions = list(db.quiz_questions.find())
        # Create a map using the new question ID format (q1, q2, etc.)
        question_map = {}
        for i, q in enumerate(questions):
            question_id = f"q{i + 1}"
            question_map[question_id] = q
        
        for answer in answers:
            question_id = answer.get('question_id')
            selected_option = answer.get('selected_option', 1) - 1  # Convert to 0-based index
            
            if question_id in question_map:
                question = question_map[question_id]
                options = question.get('options', [])
                if 0 <= selected_option < len(options):
                    brain_type = options[selected_option].get('brain_type', '')
                    if brain_type in brain_type_counts:
                        brain_type_counts[brain_type] += 1
        
        # Determine dominant brain type
        dominant_brain_type = max(brain_type_counts, key=brain_type_counts.get)
        total_answers = sum(brain_type_counts.values())
        confidence_score = (brain_type_counts[dominant_brain_type] / total_answers) * 100 if total_answers > 0 else 0
        
        # Update user's brain type
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'brain_type': dominant_brain_type, 'updated_at': datetime.utcnow()}}
        )
        
        # Generate roadmap using roadmap generator
        from roadmap_generator import RoadmapGenerator
        generator = RoadmapGenerator()
        
        # Get topic from preferences or use a more relevant default
        topic = preferences.get('topic', 'Python Programming')  # Changed from 'Data Science'
        duration = preferences.get('duration', 'intermediate')  # Standardized naming
        intensity = preferences.get('intensity', 'intermediate')  # Standardized naming
        
        roadmap = generator.generate_roadmap(
            user_id=user_id,
            topic=topic,
            brain_type=dominant_brain_type,
            duration=duration,
            intensity=intensity
        )
        
        # Brain type descriptions
        brain_type_descriptions = {
            'Visual': {
                'description': 'You learn best through visual aids like diagrams, charts, and videos.',
                'learning_tips': [
                    'Use mind maps and flowcharts',
                    'Watch educational videos',
                    'Use colorful notes and highlighters',
                    'Create visual associations'
                ],
                'strengths': ['Pattern recognition', 'Spatial awareness', 'Visual memory']
            },
            'Auditory': {
                'description': 'You learn best through listening and verbal instruction.',
                'learning_tips': [
                    'Listen to podcasts and lectures',
                    'Discuss topics with others',
                    'Read aloud',
                    'Use verbal repetition'
                ],
                'strengths': ['Verbal communication', 'Listening skills', 'Music appreciation']
            },
            'ReadWrite': {
                'description': 'You learn best through reading and writing activities.',
                'learning_tips': [
                    'Take detailed notes',
                    'Create lists and outlines',
                    'Read extensively',
                    'Write summaries'
                ],
                'strengths': ['Written communication', 'Research skills', 'Critical analysis']
            },
            'Kinesthetic': {
                'description': 'You learn best through hands-on activities and movement.',
                'learning_tips': [
                    'Practice with real examples',
                    'Use hands-on activities',
                    'Take breaks for movement',
                    'Build projects'
                ],
                'strengths': ['Problem-solving', 'Practical application', 'Physical coordination']
            }
        }
        
        response = {
            'message': 'Quiz completed successfully! Your personalized learning roadmap has been generated.',
            'assessment_results': {
                'brain_type': dominant_brain_type,
                'confidence_score': round(confidence_score, 1),
                'brain_type_distribution': brain_type_counts,
                'total_questions_answered': total_answers
            },
            'brain_type_description': brain_type_descriptions.get(dominant_brain_type, {}),
            'roadmap': {
                'roadmap_id': roadmap.get('roadmap_id', ''),
                'topic': roadmap['topic'],
                'estimated_completion_weeks': roadmap['estimated_completion_weeks'],
                'daily_time_minutes': roadmap['daily_time_minutes'],
                'total_steps': len(roadmap['steps'])
            },
            'next_steps': [
                'Review your personalized roadmap',
                'Start with the first learning step',
                'Track your progress as you complete each step',
                'Adjust your learning pace as needed'
            ]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Quiz submission error: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    question = {
        "text": data["text"],
        "options": data["options"],
        "updated_at": datetime.utcnow()
    }
    result = db.quiz_questions.insert_one(question)
    return jsonify({"id": str(result.inserted_id)}), 201

@quiz_bp.route('/questions/<id>', methods=['PUT'])
def edit_question(id):
    data = request.json
    update = {"$set": {
        "text": data.get("text"),
        "options": data.get("options"),
        "updated_at": datetime.utcnow()
    }}
    db.quiz_questions.update_one({"_id": ObjectId(id)}, update)
    return jsonify({"msg": "Updated"}), 200

@quiz_bp.route('/questions/<id>', methods=['DELETE'])
def delete_question(id):
    db.quiz_questions.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "Deleted"}), 200
