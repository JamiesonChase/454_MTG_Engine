# standard library imports
import asyncio

from flask import Flask, url_for, render_template, request, redirect
from flask_login import login_user, LoginManager, login_required, logout_user
from flask_bcrypt import Bcrypt
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

# internal app imports
from config import db_key, app_key
from models import db, User, Deck, Card, DeckCards
from forms import LoginForm, RegisterForm
from whoosh_index import indexData
from sqlite_functions import populateDB
 

# configure the main app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_key
app.config['SECRET_KEY'] = app_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)   # for hashing passwords


# configure the sqlite database
db.app = app
db.init_app(app)
db.create_all()   # creates the tables defined by the models in models.py


# configure the flask_login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'        # default page when user tries to access a page before logging in
app.config['USE_SESSION_FOR_NEXT'] = True # remove the blocked route from the url


# callback for verifying the user when a request is made
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# login page
@app.route('/login', methods=('GET','POST'))
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))

    return render_template('login.html', form=form)


# logout page, immediately redirects to the login page
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


# register page for creating new user
@app.route('/register', methods=('GET','POST'))
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# home page: this will run on startup, renders home.html
@app.route('/', methods=('GET','POST'))
@login_required
def home():
    if request.method == 'POST': # processes post request from searching
        q = request.form['q']
        if len(q) > 0:
            return redirect(url_for('results',q=q)) # only search if the user entered something

    return render_template('home.html') #renders main homepage


# results page, shown after submitting a search on the main page
@app.route('/results', methods=('GET','POST'))
@login_required
def results():
    if request.method == 'POST': # processes post request from searching
        q = request.form['q']
        if len(q) > 0:
            return redirect(url_for('results',q=q))

    search = request.args['q'] # getting the text from the query
    cards = []

    q = MultifieldParser(['name', 'desc'], schema=ix.schema).parse(search)

    with ix.searcher() as s:
        results = s.search_page(q, 1, pagelen=12)
        for result in results:
            cards.append(dict(result))

    return render_template('results.html', msg=search, cards=cards)


# individual card page, shows all stats for 1 card and suggestions for other cards
@app.route('/card/<card_id>')
@login_required
def card_page(card_id):
    SUGGESTIONS_LIMIT = 4
    card = {}
    suggestions = []

    query = QueryParser('id', schema=ix.schema).parse(card_id)
    with ix.searcher() as s:
        results = s.search(query)
        for result in results:
            if result['id'] == card_id:
                card = dict(result)
                break
        else:
            return '<h1>404 Page Not Found</h1>'

    # find suggestions based on the most popular cards in decks that
    # the current card appears in
    db_card = Card.query.filter(card['name']==Card.name).first()
    if db_card:
        # print(f'card {card["id"]} found in db, card.id = {db_card.id}, card.name = {db_card.name}')

        decks_subq = (db.session
            .query(Deck)
            .join(DeckCards, Deck.id==DeckCards.deck_id)
            .filter(DeckCards.card_id==db_card.id)
            .subquery()
        )
        top_cards = (db.session
            .query(Card)
            .join(DeckCards, Card.id==DeckCards.card_id)
            .filter(DeckCards.deck_id==decks_subq.c.id)
            .filter(Card.id != db_card.id)
            .order_by(DeckCards.count.desc())
            .limit(SUGGESTIONS_LIMIT + 1)   # get 1 extra in case current card gets filtered out
        )

        for top_card in top_cards:
            query = QueryParser('name', schema=ix.schema).parse(top_card.name)
            with ix.searcher() as s:
                results = s.search(query, limit=10)   # try the 1st 10 cards, reduce if slow
                for result in results:
                    if result['name'] == top_card.name:
                        suggestions.append(result)
                        break

    numSuggestions = len(suggestions)
    if numSuggestions < SUGGESTIONS_LIMIT:
        # the card doesn't appear in any decks or not enough suggestions were found,
        # find suggestions based on other card's that have a similar description
        # to the current card, ranked using BM25

        query = MultifieldParser(['desc', 'name'], schema=ix.schema,
            group=OrGroup).parse(card['desc'])
        with ix.searcher() as s:
            results = s.search(query)
            for result in results:
                if result['id'] == card_id:
                    continue
                suggestions.append(dict(result))
                if len(suggestions) == SUGGESTIONS_LIMIT:
                    break

    return render_template('card.html', card=card, suggestions=suggestions)


# decks page, shows list of pre-made and custom decks
@app.route('/decks', methods=('GET', 'POST'))
@login_required
def decks():
    decks = []
    for deck_result in Deck.query.all():
        deck = {}
        deck['id'] = deck_result.id
        deck['name'] = deck_result.name
        cards_main = []
        cards_sideboard = []

        deck_cards_results = (db.session
            .query(DeckCards,Card)
            .join(Card, DeckCards.card_id==Card.id)
            .filter(DeckCards.deck_id==deck_result.id)
            .all()
        )

        for data, card in deck_cards_results:
            card_data = {
                'id': card.id,
                'name': card.name,
                'count': data.count
            }
            if not data.sideboard:
                cards_main.append(card_data)
            else:
                cards_sideboard.append(card_data)

        deck['main'] = cards_main
        deck['sideboard'] = cards_sideboard
        decks.append(deck)

    return render_template('decks.html', decks=decks)


async def main():
    global ix
    tasks = await asyncio.gather(indexData(), populateDB(db))
    ix = tasks[0]
    app.run(debug=True)


# entry point to the application
if __name__ == '__main__':
    asyncio.run(main())