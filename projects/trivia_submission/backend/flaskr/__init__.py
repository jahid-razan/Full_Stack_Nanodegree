import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={"/": {"origins": "*"}})

    # after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # endpoint to handle GET requests for all available categories
    # should return a list of all the categories and the total
    # number of categories
    @app.route('/categories', methods=["GET"])
    def get_specific_cat():
        all_cat = Category.query.order_by(Category.id).all()
        total_categories = len(all_cat)
        formatted_categories = {
            category.id: category.type for category in all_cat}

        if len(all_cat) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': formatted_categories,
            "total_categories": total_categories

        })

    # GET requests for questions, including pagination (every 10 questions).
    # this endpoint returns a list of questions, number of total questions,
    # current category, and all the available categories

    @app.route('/questions', methods=["GET"])
    def get_questions():

        selection = Question.query.order_by(
            Question.id, Question.category).group_by(
            Question.category, Question.id).all()

        total_questions = len(selection)

        current_questions = paginate_questions(request, selection)
        all_cat = Category.query.order_by(Category.id).all()
        formatted_categories = {
            category.id: category.type for category in all_cat}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            "status_code": 200,
            'current_category': None,
            'categories': formatted_categories,
            'questions': current_questions,
            "total_questions": total_questions
        })

    # endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:id>', methods=['GET', 'DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            total_questions = len(selection)

            return jsonify({
                'success': True,
                "status_code": 200,
                'deleted': id,
                "total_questions": total_questions
            })
        except BaseException:
            abort(422)

    # endpoint to create a new question
    @app.route('/questions/create', methods=["POST"])
    def create_question():
        body = request.get_json()
        new_question = body.get('question')
        ans_text = body.get('answer')
        new_category = body.get('category')
        difficulty_score = body.get('difficulty')

        if not (new_question and ans_text
                and new_category and difficulty_score):
            abort(422)

        try:
            question = Question(question=new_question,
                                answer=ans_text,
                                category=new_category,
                                difficulty=difficulty_score)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            total_questions = len(selection)
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                "status_code": 200,
                'created': question.id,
                "total_questions": total_questions
            })
        except BaseException:
            abort(422)

    # GET endpoint to get questions based on category
    # returns all the questions and the total number of questions
    # for a specific category

    @app.route('/categories/<int:id>/questions')
    def search_question_cat(id):

        selection = Question.query.filter(Question.category == str(id)).all()
        total_questions = len(selection)

        current_category = Category.query.filter(
            Category.id == id).first_or_404().format()['type']

        if len(selection) == 0:
            abort(404)

        try:
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                "status_code": 200,
                'questions': current_questions,
                "total_questions": total_questions,
                "current_category": current_category
            })
        except BaseException:
            abort(422)

    # endpoint to get questions based on a search term
    @app.route('/questions/search', methods=['POST'])
    def search_question():

        body = request.get_json()
        search_term = body.get('searchTerm')

        selection = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

        if len(selection) == 0:
            abort(404)

        try:
            current_questions = paginate_questions(request, selection)
            total_questions = len(selection)

            return jsonify({
                'success': True,
                "status_code": 200,
                'questions': current_questions,
                "total_questions": total_questions
            })
        except BaseException:
            abort(422)

    # endpoint to play the quiz
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        # get the json objet
        body = request.get_json()
        prev_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)

        if body is None or quiz_category is None:
            abort(400)

        # if All categories are selected that get all the questions
        # else, when a specific category is selected, select only the
        # questions of that category that are not in previous questions
        if quiz_category['id'] == 0:
            questions = Question.query.filter(
                Question.id.notin_(prev_questions)).all()
        else:
            questions = Question.query.filter(
                Question.id.notin_(prev_questions),
                Question.category == quiz_category['id']).all()

        if len(questions) == 0:
            return jsonify({
                'success': True
            })

        if questions is None:
            abort(404)

        # get a random question from the question list already fitlered
        # by category id and the they are not in the previous questions
        current_question = random.choice(questions).format()

        return jsonify({
            'success': True,
            "status_code": 200,
            'question': current_question

        })

    # status codes and error messages
    #

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': '''Oops, Somethis went wrong. The server ecnountered
                    an internal error or misconfiguration \n and was unable
                    to process your request. \n Please try again later.'''
        }), 500

    return app
