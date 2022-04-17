from flask_sqlalchemy import inspect
import json

from config import deck_data
from models import db, User, Deck, Card, DeckCards

async def populateDB(db):
    rows = len(Deck.query.all()) + len(Card.query.all())
    if rows > 0:   # check if anything is in the tables before inserting data
        return

    with open(deck_data, 'r') as f:
        data = json.load(f)

    decks = []
    cards = []
    cards_by_deck = {}

    for deck in data:
        deck_name = deck['url']   # need to assign a name somehow to these pre-made decks
        decks.append(Deck(name=deck_name))
        cards_in_deck = []

        for card in deck['main']:
            card['sideboard'] = False
            if card['name'] not in cards:
                cards.append(Card(name=card['name']))
            cards_in_deck.append(card)

        if 'sideboard' in deck:
            for card in deck['sideboard']:
                card['sideboard'] = True
                if card['name'] not in cards:
                    cards.append(Card(name=card['name']))
                cards_in_deck.append(card)

        cards_by_deck[deck_name] = cards_in_deck

    db.session.add_all(decks)
    db.session.add_all(cards)
    db.session.commit()

    deck_cards_to_add = []
    for url, cards in cards_by_deck.items():
        deck = Deck.query.filter_by(name=url).first()
        
        for card_to_add in cards:
            card = Card.query.filter_by(name=card_to_add['name']).first()
            deck_card = DeckCards(deck_id=deck.id, card_id=card.id,
                count=card_to_add['count'], sideboard=card_to_add['sideboard'])
            deck_cards_to_add.append(deck_card)
    
    db.session.add_all(deck_cards_to_add)
    db.session.commit()