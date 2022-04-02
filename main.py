import os
import json
from flask import Flask, url_for, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.fields import Schema, TEXT, ID
import secret_keys


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = secret_keys.cookie_key
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)],
                           render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=20)],
                             render_kw={'placeholder': 'Password'})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username = username.data).first()
        if existing_user_username:
            raise ValidationError('Username taken. Please enter a new one')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)],
                           render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=20)],
                             render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')


@app.route('/', methods=('GET','POST')) # this will run on startup, renders home.html
#@login_required
def home():
    # if 'username' not in session:
    #     return redirect(url_for('login'))
    if request.method == 'POST': #processes post request from searching
        q = request.form['q']
        return redirect(url_for('results',q=q))

    return render_template('home.html') #renders main homepage


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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


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


@app.route('/results', methods=('GET','POST'))
def results():
    if request.method == 'POST': # processes post request from searching
        q = request.form['q']
        return redirect(url_for('results',q=q))

    Search = request.args['q'] # getting the text from the query
    cards = []

    q = MultifieldParser(['name', 'desc'], schema=ix.schema)
    q = q.parse(Search)

    with ix.searcher() as s:
        results = s.search_page(q, 1, pagelen=12)
        print(results[0:12])
        for result in results:
            cards.append({
                'image_url':result['image_url'],
                'url':result['url']
            })

    print(cards)
    return render_template('results.html',msg=Search,card=cards) #renders results page, passing cards and query.


if __name__ == '__main__':
    with open('test.json') as f:
        data = json.load(f)

    schema = Schema(name=TEXT(stored=True),
                    id=TEXT(stored = True),
                    desc=TEXT(stored = True),
                    url=TEXT(stored = True),
                    image_url=TEXT(stored = True))

    # create empty index directory

    if not os.path.exists('index_dir'):
        os.mkdir('index_dir')

    ix = index.create_in('index_dir', schema)
    writer = ix.writer()

    for i in range(len(data)):
        writer.add_document(name=data[i]['name'],
                            id = data[i]['id'],
                            desc=data[i]['desc'],
                            url=data[i]['url'],
                            image_url=data[i]['image_url'])
    writer.commit()

    app.run(debug=True) # run flask application