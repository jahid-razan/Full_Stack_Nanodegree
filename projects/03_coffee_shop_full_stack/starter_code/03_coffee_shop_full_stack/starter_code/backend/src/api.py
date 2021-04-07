import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from jose import jwt


from .database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)




'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


# after_request decorator to set Access-Control-Allow
@app.after_request 
def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    all_drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in all_drinks]

    return jsonify(
        {'success': True,
         'status_code': 200,
         'drinks': formatted_drinks
         })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks_detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_details(payload):
    all_drinks = Drink.query.all()
    formatted_details = [drink.long() for drink in all_drinks]

    return jsonify ({
        'success':True,
        'status_code':200,
        'drinks':formatted_details
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/new_drinks', methods=['POST'])
@requires_auth('post:drinks')
def new_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None) 
    
    if body is None:
        anort(404)

    if not (title and recipe):
        abort(422)

    try: 
        new_drink = Drink(title = title,
                          recipe = json.dumps(recipe))
        drink = [new_drink.long()]
        new_drink.insert()
    
    except BaseException:
        abort(422)

    return jsonify({
            'success':True,
            'drink': drink,
            'status_code': 200,

        })

    
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(id):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    drink = Drink.query.filter(Drink.id == int(id)).one_or_none()

    if drink is None:
        abort(404)
    
    try: 
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()
        drink = [drink.long()]

    
    except BaseException:
        abort(422)

    return jsonify({
            'success':True,
            'drinks': drink,
            'status_code': 200,
        })
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    drink = Drink.query.filter(Drink.id == int(id)).one_or_none()

    if drink is None:
        abort(404)
    
    try:
        drink.delete()

    except BaseException:
        abort(422)

    return jsonify({

        'success': True,
        'delete': id
    })



## Error Handling
'''
Example error handling for unprocessable entity
'''


# status codes and error messages   
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
        }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success":False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        "success":False,
        "error": 403,
        "message": "forbidden"
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
        }), 405



@app.errorhandler(422)
def not_found(error):
    return jsonify({
        "success":False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server(error):
    return jsonify({
    'success': False,
    'error': 500, 
    'message': ''' 
    The server ecnountered an internal error or misconfiguration.
    Please try again later.'''
        }), 500

@app.errorhandler(AuthError)
def authentification_failed(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "authentification fails"
                    }), error.status_code






'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
# ref: https://github.com/jungleBadger/udacity_coffee_shop/blob/master/troubleshooting/generate_token.md#step-13---start-your-frontend