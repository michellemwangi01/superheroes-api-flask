#!/usr/bin/env python3
import datetime
from flask import Flask
from flask_cors import CORS
import secrets
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask import make_response, request, jsonify
from flask_restx import Resource, Api, Namespace, fields
from models import db, HeroPower, Hero, Power
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

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
powers = Namespace("powers")
hero_powers = Namespace("hero powers")
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
power_model = api.model('power', {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "heroes": fields.List(fields.Nested(heroes_model))
})
power_input_model = api.model('power_input', {
    "name": fields.String,
    "description": fields.String
})
hero_input_model = api.model('hero_input', {
    "name": fields.String,
    "super_name": fields.String
})
hero_powers_model = api.model('hero_powers_model', {
    "id": fields.Integer,
    "hero_id": fields.Integer,
    "power_id": fields.Integer,
    "strength": fields.String
})
hero_powers_input_model = api.model('hero_powers_input_model', {
    "hero_id": fields.Integer,
    "power_id": fields.Integer,
    "strength": fields.String
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

    @heroes.expect(hero_input_model)
    @heroes.marshal_with(hero_model)
    def post(self):
        print(heroes.payload)
        new_hero = Hero(
            name=heroes.payload['name'],
            super_name=heroes.payload['super_name']
        )
        db.session.add(new_hero)
        db.session.commit()
        return new_hero, 201


@heroes.route('/heroes/<int:id>')
class HeroesByID(Resource):
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

    @heroes.expect(hero_input_model)
    @heroes.marshal_with(heroes_model)
    def patch(self, id):
        hero = Hero.query.filter_by(id=id).first()
        for attr in heroes.payload:
            setattr(hero, attr, heroes.payload[attr])
        db.session.add(hero)
        db.session.commit()
        return hero, 201

    def delete(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if hero:
            db.session.delete(hero)
            db.session.commit()
            response_body = {
                "delete_successful": True,
                "message": "Deleted Successfully"
            }
            return response_body, 200
        else:
            response_body = {
                "error": "Hero not found"
            }
            return response_body, 404


@powers.route('/powers')
class Powers(Resource):
    @powers.marshal_list_with(powers_model)
    def get(self):
        return Power.query.all()

    @powers.expect(power_input_model)
    @powers.marshal_with(power_model)
    def post(self):
        print(powers.payload)
        new_power = Power(
            name=powers.payload['name'],
            description=powers.payload['description']
        )
        db.session.add(new_power)
        db.session.commit()
        return new_power, 201


@powers.route('/power/<int:id>')
class PowersByID(Resource):
    @powers.marshal_with(power_model)
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if power:
            return power, 200
        else:
            return {"error": "Power not found"}, 404

    @powers.expect(power_input_model)
    @powers.marshal_with(powers_model)
    def patch(self, id):
        power = Power.query.filter_by(id=id).first()
        if power:
            for attr in powers.payload:
                setattr(power, attr, powers.payload[attr])
            try:
                db.session.add(power)
                db.session.commit()
                return power, 201
            except SQLAlchemyError as e:
                db.session.rollback()
                response = {
                    "errors": f'{e}'
                }
                return response, 404
        else:
            response = {
                "error": "Power not found"
            }
            return response, 404

    def delete(self, id):
        power = Power.query.filter_by(id=id).first()
        if power:
            db.session.delete(power)
            db.session.commit()
            response_body = {
                "delete_successful": True,
                "message": "Deleted Successfully"
            }
            return response_body, 200
        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return response_body, 404


@hero_powers.route('/hero_powers')
class HeroPowers(Resource):
    @hero_powers.marshal_list_with(hero_powers_model)
    def get(self):
        return HeroPower.query.all(), 200

    @hero_powers.expect(hero_powers_model)
    @hero_powers.marshal_with(hero_model)
    def post(self):
        try:
            new_hero_power = HeroPower(
                hero_id=hero_powers.payload['hero_id'],
                power_id=hero_powers.payload['power_id'],
                strength=hero_powers.payload['strength']
            )
            db.session.add(new_hero_power)
            db.session.commit()
            hero = Hero.query.filter_by(id=new_hero_power.hero_id).first()
            return hero, 201
        except Exception as e:
            response = {
                "errors": f'{e}'
            }
            return response, 404


@hero_powers.route('/hero_powers/<int:id>')
class HeroPowersByID(Resource):
    @hero_powers.marshal_with(hero_powers_model)
    def get(self, id):
        hero_power = HeroPower.query.filter_by(id=id).first()
        if hero_power:
            return hero_power, 200
        else:
            return {"error": "hero power not found"}, 404

    @hero_powers.expect(hero_powers_input_model)
    @hero_powers.marshal_with(hero_model)
    def patch(self, id):
        hero_power = HeroPower.query.filter_by(id=id).first()
        if hero_power:
            for attr in hero_powers.payload:
                setattr(hero_power, attr, hero_powers.payload[attr])
            db.session.add(hero_power)
            db.session.commit()
            hero = Hero.query.filter_by(id=Hero.id).first()
            return hero, 201
        else:
            return {"message": "hero power not found."}, 404

    def delete(self, id):
        hero_power = HeroPower.query.filter_by(id=id).first()
        if hero_power:
            db.session.delete(hero_power)
            db.session.commit()
            response_body = {
                "delete_successful": True,
                "message": "Deleted Successfully"
            }
            return response_body, 200
        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return response_body, 404


if __name__ == '__main__':
    app.run(port=5555, debug=True)
