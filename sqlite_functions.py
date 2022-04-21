from flask_sqlalchemy import inspect
import json

from config import deck_data, card_data
from models import Deck, Card, DeckCards

async def populateDB(db):
    # check if anything is in the tables before inserting data
    # don't overwrite data, delete database.db to recreate databse
    rows = len(Deck.query.all()) + len(Card.query.all())
    if rows > 0:
        return

    with open(card_data, 'r') as card_file:
        data = json.load(card_file)
    
    # read in all the cards first, adding them to the Card table
    # map the names to their id to relate them to cards in the decks
    cards = []
    card_ids = {}
    for card in data:
        cards.append(Card(
            id        = int(card['id']),
            name      = card['name'],
            url       = card['url'],
            image_url = card['image_url'],
            power     = card['power'],
            toughness = card['toughness'],
            rarity    = card['rarity'],
            colors    = card['colors'],
            cost      = card['cost']
        ))
        card_ids[card['name']] = int(card['id'])

    # read in the decks, splitting them into Deck and DeckCards
    # only add them to DeckCards if they exist in Cards
    with open(deck_data, 'r') as deck_file:
        data = json.load(deck_file)

    decks = []
    deck_cards = []

    for i, deck in enumerate(data):
        decks.append(Deck(id=i))

        # get all the cards in the deck
        # only consider main decks, ignore sideboards unless we have time
        for card in deck['main']:
            # throw out cards not in Cards since they won't have an id
            if card['name'] not in card_ids:  
                continue
            deck_cards.append(DeckCards(
                deck_id = i,
                card_id = card_ids[card['name']],
                count   = card['count']
            ))

    db.session.add_all(decks)
    db.session.add_all(cards)
    db.session.add_all(deck_cards)
    db.session.commit()