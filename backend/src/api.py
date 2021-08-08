import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
Uncommenting the following line to initialize the datbase
!! WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
GET /drinks
Public endpoint.

- Contains only the drink.short() data representation.
- Returns status code 200 and json {"success": True, "drinks": drinks}
where drinks is the list of drinks or appropriate status code indicating
reason for failure.
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()

    if not drinks:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    }), 200


'''
GET /drinks-detail
Requires the 'get:drinks-detail' permission.

- Contains the drink.long() data representation.
- Returns status code 200 and json {"success": True, "drinks": drinks}
where drinks is the list of drinks
or appropriate status code indicating reason for failure.
'''


@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    drinks = Drink.query.all()

    if not drinks:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    }), 200


'''
POST /drinks
Requires the 'post:drinks' permission.

- Creates a new row in the drinks table.
- Contains the drink.long() data representation.
- Returns status code 200 and json {"success": True, "drinks": drink}
where drink an array containing only the newly created drink
or appropriate status code indicating reason for failure.
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drink(jwt):
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')
    new_drink = Drink(title=title, recipe=json.dumps(recipe))

    try:
        new_drink.insert()
        return jsonify({
            "success": True,
            "drink": [new_drink.long()]
        }), 200

    except Exception as err:
        print(err)
        abort(405)


'''
PATCH /drinks/<id> - where <id> is the existing model id
Requires the 'patch:drinks' permission.

- Responds with a 404 error if <id> is not found.
- Updates the corresponding row for <id>.
- Contains the drink.long() data representation.
- Returns status code 200 and json {"success": True, "drinks": drink}
where drink an array containing only the updated drink
or appropriate status code indicating reason for failure.
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    if title:
        drink.title = title

    if recipe:
        drink.recipe = json.dumps(recipe)

    try:
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200

    except Exception as err:
        print(err)
        abort(405)


'''
DELETE /drinks/<id> - where <id> is the existing model id
Require the 'delete:drinks' permission.

- Responds with a 404 error if <id> is not found.
- Deletes the corresponding row for <id>.
- Returns status code 200 and json {"success": True, "delete": id}
where id is the id of the deleted record
or appropriate status code indicating reason for failure.
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.get(drink_id)

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id,
        }), 200

    except Exception as err:
        print(err)
        abort(422)


'''
Error Handling
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


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
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def invalid_method(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "invalid method"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "server error"
    }), 500
