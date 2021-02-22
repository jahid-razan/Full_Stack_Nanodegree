import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None): 
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

      
    # after_request decorator to set Access-Control-Allow
    @app.after_request 
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # endpoint to handle GET requests for all available categories                
    @app.route('/categories', methods=["GET"])
    def get_specific_cat():
        all_cat = Category.query.order_by(Category.id).all()
        total_categories = len(all_cat)
        formatted_categories = {category.id:category.type for category in all_cat}

          
        if len(all_cat) == 0:
            abort(404)
          
        return jsonify({
            'success':True,
            'categories': formatted_categories,
            "total_categories": total_categories

                    })
     
      
    # GET requests for questions, including pagination (every 10 questions). 
    # this endpoint returns a list of questions, number of total questions, 
    # current category, and all the available categories
    @app.route('/questions', methods=["GET"])
    def get_questions():
        selection = Question.query.order_by(Question.id, Question.category).group_by(Question.category, Question.id).all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)
        all_cat = Category.query.order_by(Category.id).all()
        formatted_categories = {category.id:category.type for category in all_cat}
          
        if len(current_questions) == 0:
            abort(404)
          
        return jsonify({
                        'success':True,
                        "status_code":200,
                        'current_category': None,
                        'categories': formatted_categories,
                        'questions': current_questions,
                        "total_questions": total_questions
                    })

    
    
    # endpoint to DELETE question using a question ID.                
    @app.route('/questions/<int:id>', methods=["DELETE"])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).first_or_404()
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            total_questions = len(selection)
            
            return jsonify({
                'success':True,
                "status_code":200,
                'deleted': id,
                "total_questions": total_questions
                })
        except:
            abort(422)
     
    
    @app.route('/questions/create', methods=["POST"])
    def create_question():
        body = request.get_json()
        new_question = body.get('question')
        ans_text = body.get('answer')
        new_category = body.get('category')
        difficulty_score = body.get('difficulty')


        if not (new_question and ans_text and new_category and difficulty_score):
            abort(422)

        try:
            question = Question( question = new_question, 
                                 answer = ans_text, 
                                 category = new_category,
                                 difficulty = difficulty_score)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            total_questions = len(selection)
            current_questions = paginate_questions(request, selection)
            
            return jsonify({
                    'success':True,
                    "status_code":200,
                    'created': question.id,
                    "total_questions": total_questions
                    })
        except:
            abort(422)

    # GET endpoint to get questions based on category
    # returns all the questions and the total number of questions 
    # for a specific category


    @app.route('/categories/<int:id>/questions')

    def search_question_cat(id):

        selection = Question.query.filter(Question.category == str(id)).all()
        total_questions = len(selection)
        
        current_category = Category.query.filter(Category.id == id).first_or_404().format()['type']
        

        if len(selection) == 0:
            return abort(404)

        try:
            current_questions = paginate_questions(request, selection)
            
            return jsonify({
                    'success':True,
                    "status_code":200,
                    'questions': current_questions,
                    "totalQuestions": total_questions,
                    "currentCategory": current_category
                    })
        except:
            abort(422)

    # endpoint to get questions based on a search term
    @app.route('/questions/search', methods=['POST'])

    def search_question():

        body = request.get_json()

        search_term = body.get('searchTerm') 
        print(search_term)
        

        if not search_term:
            abort(422)

        try:
            selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            total_questions = len(selection)
            

            if len(selection) == 0:
                return abort(404)
            current_questions = paginate_questions(request, selection)
            
            return jsonify({
                    'success':True,
                    "status_code":200,
                    'questions': current_questions,
                    "total_questions": total_questions
                    })
        except:
            abort(422)

    # endpoint to play the quiz
    @app.route('/quizzes', methods=['POST'])

    def quiz():
        # get the json objet
        body = request.get_json()
        prev_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)


        if body is None or quiz_category is None:
            abort(404)

        # if All categories are selected that get all the questions
        # else, when a specific category is selected, select only the 
        # questions of that category that are not in previous questions
        if quiz_category['id'] == 0:
            questions = Question.query.filter(Question.id.notin_(prev_questions)).all()
        else:
            questions = Question.query.filter(Question.id.notin_(prev_questions),
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
                    'success':True,
                    "status_code":200,
                    'question': current_question

                    })

       

        
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success":False,
            "error": 404,
            "message": "resource not found"
        }), 404

   
    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success":False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
          }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
          "success": False,
          "error": 405,
          "message": "Method Not Allowed"
          }), 405

    return app




'''
@TODO: 
.
'''



'''
@TODO: 
Create an endpoint to handle GET requests for questions, 
including pagination (every 10 questions). 
This endpoint should return a list of questions, 
number of total questions, current category, categories. 

TEST: At this point, when you start the application
you should see questions and categories generated,
ten questions per page and pagination at the bottom of the screen for three pages.
Clicking on the page numbers should update the questions. 
'''

'''
@TODO: 
Create an endpoint to DELETE question using a question ID. 

TEST: When you click the trash icon next to a question, the question will be removed.
This removal will persist in the database and when you refresh the page. 
'''

'''
@TODO: 
Create an endpoint to POST a new question, 
which will require the question and answer text, 
category, and difficulty score.

TEST: When you submit a question on the "Add" tab, 
the form will clear and the question will appear at the end of the last page
of the questions list in the "List" tab.  
'''

'''
@TODO: 
Create a POST endpoint to get questions based on a search term. 
It should return any questions for whom the search term 
is a substring of the question. 

TEST: Search by any phrase. The questions list will update to include 
only question that include that string within their question. 
Try using the word "title" to start. 
'''

'''
@TODO: 
Create a GET endpoint to get questions based on category. 

TEST: In the "List" tab / main screen, clicking on one of the 
categories in the left column will cause only questions of that 
category to be shown. 
'''


'''
@TODO: 
Create a POST endpoint to get questions to play the quiz. 
This endpoint should take category and previous question parameters 
and return a random questions within the given category, 
if provided, and that is not one of the previous questions. 

TEST: In the "Play" tab, after a user selects "All" or a category,
one question at a time is displayed, the user is allowed to answer
and shown whether they were correct or not. 
'''

'''
@TODO: 
Create error handlers for all expected errors 
including 404 and 422. 
'''

  

