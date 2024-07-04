import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    database_path = 'postgresql://{}@{}/{}'.format('postgres:postgres', 'localhost:5432', 'trivia')
    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    CORS(app, resources={r"/*": {"origins": "*"}})
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    
    @app.route('/categories')
    def get_categories():
        selection = Category.query.order_by(Category.id).all()
        current_categories = {}
        for category in selection:
            current_categories[category.id] = category.type
    
        if len(current_categories) == 0:
            abort(404)
    
        return jsonify({
            'success': True,
            'categories': current_categories,
            'total_categories': len(Category.query.all()),
            })
        
    
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.all()
        form_questions = [question.format() for question in questions]
        return jsonify({
            'questions': form_questions[start:end],
            'total_questions': len(form_questions),
            'success': True
        })
    

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        question.delete()
        return jsonify({
            'success': True
        })
    

    @app.route('/questions', methods=['POST'])
    def add_question():
        question = request.json.get('question')
        answer = request.json.get('answer')
        category = request.json.get('category')
        difficulty = request.json.get('difficulty')
        if question is None or answer is None or category is None or difficulty is None:
            abort(422)
        new_question = Question(question=question, answer=answer,category=category, difficulty=difficulty)
        new_question.insert()
        return jsonify({
            'success': True
        })
    

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.json.get('searchTerm','')
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        form_questions = [question.format() for question in questions]
        return jsonify({
            'questions': form_questions,
            'total_questions': len(form_questions),
            'success': True
        })
    

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()
        form_questions = [question.format() for question in questions]
        return jsonify({
            'questions': form_questions,
            'total_questions': len(form_questions),
            'success': True
        })
    
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        previous_questions = request.json.get('previous_questions')
        category = request.json.get('quiz_category')
        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category['id']).all()
        form_questions = [question.format() for question in questions]
        questions = [question for question in form_questions if question['id'] not in previous_questions]
        if len(questions) == 0:
            return jsonify({
                'question': None,
                'success': True
            })
        question = random.choice(questions)
        return jsonify({
            'question': question,
            'success': True
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Page Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400
    
    return app

