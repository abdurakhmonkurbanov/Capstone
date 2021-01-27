from flask_cors import CORS
from flask import (Flask, request, abort,
                   jsonify, render_template)
from flask_sqlalchemy import SQLAlchemy
# ----------------------------------------- #
from capstone import app, db
from capstone.auth.auth import auth_required, AuthError
from capstone.models import  Movie, Actor
from capstone.config import auth0_url


"""
casting-assistant@mail.com
casting-director@mail.com
casting-producer@mail.com

$Password2021
"""

def paginate(request, results):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * 10
    end = start + 10

    all_results = [result.format() for result in results]
    paginated_results = all_results[start:end]

    return paginated_results

CORS(app)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods",
                         "GET,PATCH,POST,DELETE,OPTIONS")
    return response

@app.route('/')
def login():
    return render_template('login.html', url=auth0_url)

@app.route('/login-results')
def login_res():
    return render_template('result.html')

@app.route("/actors", methods=["GET"])
@auth_required("read:actors")
def get_actors(token):
    """
    [GET]:
    - All Actor data
    """
    data = Actor.query.all()
    actors = paginate(request, data)

    if len(actors) == 0: abort(404,{"message": "OOPS! No actors willing to work"})

    return jsonify({
        "success": True,
        "actors": actors}), 200


@app.route("/movies", methods=["GET"])
@auth_required("read:movies")
def get_movies(token):
    """
    [GET]:
    - All Movie data
    """
    data = Movie.query.all()

    movies = paginate(request, data)

    if len(movies) == 0:
        abort(404,{"message": "OOPS! No one is making movies"})

    return jsonify({
        "success": True,
        "movies": movies}), 200

@app.route("/actors", methods=["POST"])
@auth_required("add:actor")
def add_actor(token):
    """
    [POST]:
    - Actor data
    """

    data = request.get_json()
    if not data.get("name"): abort(400,{"message": 'Please add "name" in the json'})

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")

    post_data = Actor(name=name, 
                     age=age, 
                     gender=gender
    )

    post_data.insert()

    return jsonify({
        "success": True,
        "actor": post_data.id}), 200


@app.route("/movies", methods=["POST"])
@auth_required("add:movie")
def add_movie(token):
    """
    [POST]:
    - Movie
    """
    data = request.get_json()

    if not data: abort(400,{"message": "there is no json body"})

    title = data.get("title")
    release_date = data.get("release_date")

    post_data = Movie(title=title, release_date=release_date)
    post_data.insert()

    return jsonify({
        "success": True,
        "movie": post_data.id}), 200


@app.route("/actors/<int:actor_id>", methods=["PATCH"])
@auth_required("modify:actor")
def modify_actor(token, actor_id):
    """
    [PATCH]:
    - Actor data
    """
    data = request.get_json()

    if not data: abort(400,{"message": "there is no json body"})
    actor_old_data = Actor.query.get(actor_id)

    if not actor_old_data: abort(404,{"message": "No actor with this id"})

    new_name = data.get("name")
    new_age = data.get("age")
    new_gender = data.get("gender")

    if new_name: actor_old_data.name = new_name

    if new_age: actor_old_data.age = new_age

    elif new_gender: actor_old_data.gender = new_gender

    actor_old_data.update()

    return jsonify({"success": True, "actor": actor_old_data.id}), 200


@app.route("/movies/<int:movie_id>", methods=["PATCH"])
@auth_required("modify:movie")
def modify_movie(token, movie_id):
    """
    [PATCH]:
    - Movie data
    """
    data = request.get_json()

    if not data: abort(400, {"message": "there is no json body"})

    old_data = Movie.query.get(movie_id)

    if not old_data: abort(404,{"message": "No movie with this id"})

    if data.get("title"): old_data.title = data.get("title")

    if data.get("release_date"): old_data.new_release_date = data.get("release_date")

    old_data.update()

    return jsonify({"success": True,
                    "movie": old_data.id}), 200


@app.route("/actors/<int:actor_id>", methods=["DELETE"])
@auth_required("delete:actor")
def delete_actor(token, actor_id):
    """
    [DELETE]:
    -Actor
    """
    actor = Actor.query.get(actor_id)

    if not actor: abort(404,{"message": "No actor with this id"})

    actor.delete()

    return jsonify({"success": True, "actor": actor.id}), 200


@app.route("/movies/<int:movie_id>", methods=["DELETE"])
@auth_required("delete:movie")
def delete_movie(token, movie_id):
    """
    [DELETE]:
    - Movie
    """
    movie = Movie.query.get(movie_id)

    if not movie: abort(404,{"message": "No movie with this id"})

    movie.delete()

    return jsonify({
            "success": True,
            "movie": movie.id}), 200


########################################
##         Error Handlers             ##
########################################

@app.errorhandler(401)
def unauthorized_401(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authentication error."
    }), 401

@app.errorhandler(403)
def forbidden_403(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden."
    }), 403

@app.errorhandler(404)
def not_found_404(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Item not found."
    }), 404

@app.errorhandler(422)
def unprocessable_402(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Request could not be processed."
    }), 422

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code
