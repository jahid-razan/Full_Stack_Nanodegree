import os
from flask import Flask, request, jsonify, abort

app = Flask(__name__)




# @app.route('/drinks', methods=['GET'])
# def get_all_drinks():
#     all_drinks = Drink.query.all()
#     formatted_drinks = [drink.short() for drink in all_drinks]

#     return jsonify(
#         {'success': True,
#          'status_code': 200,
#          'drinks': formatted_drinks
#          })

@app.route('/headers')
def headers():
    auth_header = request.headers['Authorization']
    print(auth_header)
    return 'not implimented'