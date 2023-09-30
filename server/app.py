#!/usr/bin/env python3
from flask import Flask
from flask_cors import CORS
import secrets
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask import make_response, request, jsonify
from flask_restx import Resource, Api, Namespace, fields
from models import db, HeroPower, Hero, Power

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)
heroes = Namespace("heroes")
home = Namespace("home")
powers = Namespace("Powers")
hero_powers = Namespace("Hero Powers")
api.add_namespace(home)
api.add_namespace(powers)
api.add_namespace(hero_powers)
api.add_namespace(heroes)

CORS(app)

# ----------------------- A P I _ M O D E L S -----------------------
heroes_model = api.model('heroes', {
    "id": fields.Integer,
    "name": fields.String,
    "super_name": fields.String
})
powers_model = api.model('powers', {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String
})
hero_model = api.model('hero', {
    "id": fields.Integer,
    "name": fields.String,
    "super_name": fields.String,
    "powers": fields.List(fields.Nested(powers_model))
})
power_model = api.inherit('power', powers_model, {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "heroes": fields.List(fields.Nested(heroes_model))
})


# ----------------------- A P I _ R O U T E S -----------------------

@home.route('/')
class Home(Resource):
    def get(self):
        response_message = {
            "message": "WELCOME TO THE SUPERHERO GALAXY!."
        }
        return response_message, 200


@heroes.route('/heroes')
class Heroes(Resource):
    @heroes.marshal_list_with(heroes_model)
    def get(self):
        return Hero.query.all()


@heroes.route('/heroes/<int:id>')
class Heroesbyid(Resource):
    @heroes.marshal_list_with(hero_model)
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if hero:
            return hero, 200
        else:
            response = {
                "error": "Restaurant not found"
            }, 404
        return response


@powers.route('/powers')
class Powers(Resource):
    @powers.marshal_list_with(powers_model)
    def get(self):
        return Power.query.all()


@powers.route('/power/<int:id>')
class Powersbyid(Resource):
    @powers.marshal_with(power_model)
    def get(self, id):
        return Power.query.filter_by(id=id).first(), 200

    # @hpowers.expects()
    # def patch(self):


if __name__ == '__main__':
    app.run(port=5555, debug=True)
