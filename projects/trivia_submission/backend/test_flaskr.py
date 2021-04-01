import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"

        self.DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', '1234')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia_test')
        self.DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
            self.DB_USER,
            self.DB_PASSWORD,
            self.DB_HOST,
            self.DB_NAME)

        setup_db(self.app, self.DB_PATH)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation
    and for expected errors.
    """

    def test_all_categories(self):
        """
        Test for listing the categories
        """
        # get response and load it into a variable
        res = self.client().get('/categories')
        data = json.loads(res.data)

        # check the status code and the messgae
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # check categories and total_categories variables
        # both should return values
        self.assertTrue(data['categories'], True)
        self.assertTrue(data['total_categories'], True)

    def test_error_categories(self):
        """
        Test for post method in the the categories
        which is not allowed for this endpoint
        """
        # get response and load it into a variable
        res = self.client().post('/categories', json={})
        data = json.loads(res.data)

        # check the status code and the error messgae
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_paginate_questions(self):
        """
        Test for get method to see if the
        question pagination works
        """

        # get response and load it into a variable
        res = self.client().get('/questions')
        data = json.loads(res.data)

        # check the status code and the messages
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # check the current_category- should return None
        self.assertEqual(data['current_category'], None)

        # check categories, questions and total_questions
        # variables all should return values
        self.assertTrue(data['categories'], True)
        self.assertTrue(data['questions'], True)
        self.assertTrue(data['total_questions'], True)

    def test_404_request_invalid_page(self):
        """
        Test for a page that does not exist
        """
        # get response and load it into a variable
        res = self.client().get('/questions?page=1000', json={'quesiton': 'a'})
        data = json.loads(res.data)

        # check the status code and the messages
        # since the page does not exist a well formatted request
        # should return resource not found
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_questions(self):
        """
        Test for the delete method of a question that
        exists. This method Fails once the quesiton is
        deleted and need to be given a number that is
        in the question list
        """
        # get response and load it into a variable
        res = self.client().delete('questions/53')
        data = json.loads(res.data)

        # check the status code after deletion- a succesful
        # delete should return 200 and success value as true

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # the specified question is deleted
        self.assertEqual(data['deleted'], 53)

        # return the total number of question after the deletion
        self.assertTrue(data['total_questions'], True)

    def test_book_does_not_exist(self):
        """
        Test for  the delete method of a question that
        does not exist. Should return an unprocessable error
        """

        # get response and load it into a variable
        res = self.client().delete('/questions/55')
        data = json.loads(res.data)

        # status code- should return 422 and unprocessable
        # since the question does not exist and deletion
        # should fail- therefore false value for success
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_questions(self):
        """
        Test for creating a new question
        """

        # parameters for the new question
        new_question = {
            'question': "Which 03 countries will host 2026 football worlcup?",
            'answer': 'United States, Canada and Mexico',
            'category': '6',
            'difficulty': 2}

        # get response and load it into a variable
        res = self.client().post('/questions/create', json=new_question)
        data = json.loads(res.data)

        # status code- should return 200 after successful creation
        # and success as true
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # should return true for the created variable
        # and number of total_question after the new_question
        # creation
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'], True)

    def test_if_create_questions_fails(self):
        """
        Failed Test for creating a new question attempt
        wihout assigning all the parameters
        """
        # parameters for the new question- not formatted with all required
        # parameters
        new_question = {
            'question': "Which 03 countries will host 2026 football worlcup?",
            'answer': '',
            'category': '',
            'difficulty': 2}

        # get response and load it into a variable
        res = self.client().post('/questions/create', json=new_question)
        data = json.loads(res.data)

        # status code- should return 422 and unprocessable
        # since the question creation fails
        # returns false value for success
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_questions_for_a_category(self):
        """
        Test forgetting all the questions
        for a specific category
        """
        # get response and load it into a variable
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        # status code- should return 200, total_question
        # and the name of the category
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'], True)
        self.assertTrue(data['total_questions'], True)
        self.assertTrue(data['current_category'], True)

    def test_for_a_nonexistant_category(self):
        """
        Failed test for a category that does
        not exist
        """

        # get response and load it into a variable
        res = self.client().get('/categories/12/questions')
        data = json.loads(res.data)

        # a well formatted request should return
        # status code 404 and resource not found
        # message since the category does not exist

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_question(self):
        """
        Test for finding questions with a search term
        that exists in one of the questions
        """
        # search term- 1930 exists in the question
        search_term = {"searchTerm": "1930"}

        # get response and load it into a variable
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        # status code- should return 200
        # true for success and the question
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['questions'], True)

    def test_nonexistant_search_question(self):
        """
        Test for finding questions with a search term
        that does not exist in the questions
        """
        # search term that does not exist in the quesitons
        search_term = {"searchTerm": "zzz"}

        # get response and load it into a variable
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        # a well formatted request should return
        # status code 404 and resource not found
        # message since no question contains the search term
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_quizzes(self):
        """
        Test for playing the quiz
        """

        # parameters to insert before play
        details = {'quiz_category': {'id': 2}, 'pevious_questions': [
            'La Giaconda is better known as what?']}

        # get response and load it into a variable
        res = self.client().post('/quizzes', json=details)
        data = json.loads(res.data)

        # status code-200, success true and a question
        # to indicate successful request
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'], True)

    def test_quizzes_fails(self):
        """
        Test for bad formatted request
        """

        # bad formatted parameters

        details = {}
        # get response and load it into a variable
        res = self.client().post('/quizzes', json=details)
        data = json.loads(res.data)

        # status code-400, success false and the message
        # bad request to indicate failed request
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
