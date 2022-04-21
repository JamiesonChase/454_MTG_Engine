from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class DeckCards(db.Model):
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    count = db.Column(db.Integer, nullable=False)
    card = db.relationship('Card', back_populates='decks')
    deck = db.relationship('Deck', back_populates='cards')

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('deck', uselist=False))
    cards = db.relationship('DeckCards', back_populates='deck')

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200))
    image_url = db.Column(db.String(200))
    power = db.Column(db.String(20))
    toughness = db.Column(db.String(20))
    rarity = db.Column(db.String(200))
    colors = db.Column(db.String(200))
    cost = db.Column(db.String(200))

    
    decks = db.relationship('DeckCards', back_populates='card')
