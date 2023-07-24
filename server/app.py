#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        json = request.get_json()

        try: 
            json["username"]
        except:
            return {"message": "Invalid username"}, 422
        try: 
            json["image_url"]
        except:
            return {"message": "Invalid image_url"}, 422
        else:
            user = User(
                username=json["username"],
                image_url=json["image_url"],
                bio=json["bio"]
            )
            user.password_hash = json["password"]

            db.session.add(user)
            db.session.commit()

            user_dict = {"id": user.id, "username":user.username, "image_url": user.image_url, "bio": user.bio}

            return user_dict, 201

class CheckSession(Resource):
    
    def get(self):
        user_id = session["user_id"]
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            user_dict = {"id": user.id, "username":user.username, "image_url": user.image_url, "bio": user.bio}
            return user_dict, 200
        else:
            return {"message": "Unauthorized"}, 401 

class Login(Resource):

    def post(self):

        username = request.get_json()["username"]
        user = User.query.filter(User.username == username).first()

        password = request.get_json()["password"]
        if user:
            if user.authenticate(password):
                session["user_id"] = user.id
                user_dict = {"id": user.id, "username":user.username, "image_url": user.image_url, "bio": user.bio}
                return user_dict, 200
            return {'error': 'Invalid password'}, 401
        return {'error': 'Invalid username'}, 401

class Logout(Resource):

    def delete(self):
        if session.get("user_id") is None:
            session["user_id"] = None
            return {"message": "Unauthorized"}, 401
        session["user_id"] = None
        return {}, 204

class RecipeIndex(Resource):
    
    def get(self):
        list = []
        user_id = session.get("user_id")
        if not user_id:
            return {"message": "Unauthorized"}, 401
        user = User.query.filter(User.id == user_id).first()

        for recipe in user.recipes:
            recipe_obj = {
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
            }
            list.append(recipe_obj)
        return list, 200
    
    def post(self):
        user_id = session.get("user_id")
        json = request.get_json()
        if not user_id:
            return {"message": "Unauthorized"}, 401

        try: 
            json["title"]
        except:
            return {"message": "Invalid title"}, 422
        try: 
            json["minutes_to_complete"]
        except:
            return {"message": "Invalid minutes to complete"}, 422
        else:
            if len(json["instructions"]) < 50:
                return {"message": "Invalid instructions"}, 422
            new_recipe = Recipe(
                title=json["title"],
                instructions=json["instructions"],
                minutes_to_complete=json["minutes_to_complete"]
            )
            new_recipe.user_id = user_id

            db.session.add(new_recipe)
            db.session.commit()

            new_recipe_obj = {
                "title": new_recipe.title,
                "instructions": new_recipe.instructions,
                "minutes_to_complete": new_recipe.minutes_to_complete
            }
            return new_recipe_obj, 201

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
