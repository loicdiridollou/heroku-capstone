import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth import AuthError, requires_auth
from models import db_reset, db_setup, Actor, Movie
from config import pagination

ROWS_PER_PAGE = pagination['example']

def create_app(test_config=None):
    app = Flask(__name__)
    db_setup(app)
    #db_reset()

    CORS(app)


    def paginate_results(request, selection):
        # Same function as I used in one of the previous submissions to return only X rows per page (cf Trivia API)
        page = request.args.get('page', 1, type=int)
        
        start =  (page - 1) * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE

        objects_formatted = [object_name.format() for object_name in selection]
        return objects_formatted[start:end]


    ########################################
    # Endpoints
    ########################################

    @app.route('/')
    def index_page():
        return jsonify({"message": "Healthy"})


    ########################################
    # Actors endpoints for GET, POST, PATCH, DELETE
    
    @app.route('/actors', methods=['GET'])
    @requires_auth('read:actors')
    def get_actors(payload):
        actors_raw = Actor.query.all()
        actors_paginated = paginate_results(request, actors_raw)

        if len(actors_paginated) == 0:
            abort(404)

        return jsonify({"success": True, "actors": actors_paginated}), 200


    @app.route('/actors', methods=['POST'])
    @requires_auth('create:actors')
    def insert_actors(payload):
        body = request.get_json()

        if body is None:
            abort(400)
        
        name = body.get("name")
        age = body.get("age")
        gender = body.get("gender", "Other")

        if not name or not age:
            abort(422)

        new_actor = Actor(name = name, age = age, gender = gender)
        new_actor.insert()
        
        return jsonify({"success": True, "created": new_actor.id})


    @app.route('/actors/<actor_id>', methods=['PATCH'])
    @requires_auth('edit:actors')
    def edit_actors(payload, actor_id):
        body = request.get_json()
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if body is None:
            abort(400)
        if actor is None:
            abort(400)
        
        name = body.get("name")
        age = body.get("age")
        gender = body.get("gender", "Other")

        if name:
            actor.name = name
        if age:
            actor.age = age
        if gender:
            actor.gender = gender
        
        actor.update()
        
        return jsonify({"success": True, "updated": actor.id})


    @app.route('/actors/<actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actors(payload, actor_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if not actor:
            abort(400)
        
        actor.delete()

        return jsonify({"success": True, "deleted": actor_id})


    ########################################
    # Movies endpoints for GET, POST, PATCH, DELETE

    @app.route('/movies', methods=['GET'])
    @requires_auth('read:movies')
    def get_movies(payload):
        movies_raw = Movie.query.all()
        movies_paginated = paginate_results(request, movies_raw)

        if len(movies_paginated) == 0:
            abort(404)

        return jsonify({"success": True, "actors": movies_paginated}), 200


    @app.route('/movies', methods=['POST'])
    @requires_auth('create:movies')
    def insert_movies(payload):
        body = request.get_json()

        if body is None:
            abort(400)
        
        title = body.get("title")
        release_date = body.get("release_date", "Wed, 24 Jun 2020 00:00:00 GMT")

        if not title:
            abort(422)

        new_movie = Movie(title = title, release_date = release_date)
        new_movie.insert()
        
        return jsonify({"success": True, "created": new_movie.id})
        

    @app.route('/movies/<movie_id>', methods=['PATCH'])
    @requires_auth('edit:movies')
    def edit_movies(payload, movie_id):
        body = request.get_json()
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if body is None:
            abort(400)
        if movie is None:
            abort(400)
        
        title = body.get("title")
        release_date = body.get("age")
       
        if title:
            movie.title = title
        if release_date:
            movie.release_date = release_date
        
        movie.update()
        
        return jsonify({"success": True, "updated": movie.id})


    @app.route('/movies/<movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movies(payload, movie_id):
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if not movie:
            abort(400)
        
        movie.delete()

        return jsonify({"success": True, "deleted": movie_id})



    ########################################
    # Error Handlers
    ########################################

    @app.errorhandler(422)
    def unprocessable(error):
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

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404


    @app.errorhandler(AuthError)
    def authentification_failed(AuthError):
        return jsonify({"success": False, "error": AuthError.status_code, "message": AuthError.error}), 401


    return app



app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)