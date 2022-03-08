from flask import Flask, url_for, render_template,request, redirect

app = Flask(__name__)

@app.route('/', methods=('GET','POST')) # this will run on startup, renders home.html
def home():
    if request.method == 'POST': #processes post request from searching
        q = request.form['q']
        return redirect(url_for('results',q=q))

    return render_template('home.html') #renders main homepage

@app.route('/results', methods=('GET','POST'))
def results():
    if request.method == 'POST': # processes post request from searching
        q = request.form['q']
        return redirect(url_for('results', q=q))

    Search = request.args['q'] # getting the text from the query
    cards = ['https://c1.scryfall.com/file/scryfall-cards/large/front/a/8/a8e9f4d2-bba5-4061-8ae7-a68b912f2c11.jpg?1572893504',
             'https://c1.scryfall.com/file/scryfall-cards/large/front/6/f/6f87292c-0140-44d7-881e-2e8c9ff737a1.jpg?1562917281',
             'https://c1.scryfall.com/file/scryfall-cards/normal/front/6/a/6adb7d73-4482-4930-8497-cffd169b57e2.jpg?1557576232',
             'https://c1.scryfall.com/file/scryfall-cards/normal/front/3/c/3c21df8e-a24f-4ce1-aa8a-1467f9f9423a.jpg?1562703323',
             'https://c1.scryfall.com/file/scryfall-cards/normal/front/8/1/8148adc6-7946-4abd-8601-b1f4cd6916c2.jpg?1568004013',
             'https://c1.scryfall.com/file/scryfall-cards/large/front/9/3/939a4351-3ec7-4e6c-8cdd-766bfd670391.jpg?1592709656',
             'https://c1.scryfall.com/file/scryfall-cards/large/front/8/3/83a786fa-4b86-40f7-ac58-1a05fb38fcdb.jpg?1581480687',
             'https://c1.scryfall.com/file/scryfall-cards/large/front/5/4/54153b9c-483e-4e5c-a1ab-b1c8a7a657d4.jpg?1581479206',
             'https://c1.scryfall.com/file/scryfall-cards/large/front/9/9/9990681d-b893-46d3-8bf1-6d3bbc4df767.jpg?1562925984']
    return render_template('results.html',msg=Search,card=cards) #renders results page, passing cards and query.
def main():
    app.run() # run flask application

main()