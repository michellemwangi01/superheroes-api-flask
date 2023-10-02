from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
import bcrypt

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    super_name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    heropowers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')
    powers = association_proxy('heropowers', 'power')

    def __repr__(self):
        return f'(id={self.id}, name={self.name} super_name={self.super_name})'


class Power(db.Model):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    heropowers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')
    heroes = association_proxy('heropowers', 'hero')

    def __repr__(self):
        return f'(id={self.id}, name={self.name} description={self.description})'

    @validates('description')
    def checks_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be longer than 20 chars")
        else:
            return description


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)

    def __repr__(self):
        return f'(id={self.id}, username={self.username})'

    def set_password(self, password):
        # Generate a password hash
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password_hash = password_hash.decode('utf-8')

    def check_password(self, password):
        # Check if a provided password matches the stored hash
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))




class HeroPower(db.Model):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String)
    hero_id = db.Column(db.String, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.String, db.ForeignKey('powers.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    hero = db.relationship('Hero', back_populates='heropowers')
    power = db.relationship('Power', back_populates='heropowers')

    def __repr__(self):
        return f'(id={self.id}, heroID={self.hero_id} strength={self.strength}) powerID={self.power_id}'

    @validates('strength')
    def checks_strength(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be a value either 'Strong', 'Weak' or 'Average'")
        else:
            return strength
