from flask import Flask, url_for, render_template,request, redirect
import json
from whoosh.qparser import MultifieldParser
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
import os, os.path

app = Flask(__name__)


with open('test.json') as f:
    data = json.load(f)

schema = Schema(name=TEXT(stored=True),
                id=TEXT(stored = True),
                desc=TEXT(stored = True),
                url=TEXT(stored = True),
                image_url=TEXT(stored = True))

# create empty index directory

if not os.path.exists("index_dir"):
    os.mkdir("index_dir")

ix = index.create_in("index_dir", schema)
writer = ix.writer()

for i in range(len(data)):
    writer.add_document(name=data[i]['name'],
                        id = data[i]['id'],
                        desc=data[i]['desc'],
                        url=data[i]['url'],
                        image_url=data[i]['image_url'])
writer.commit()


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
        return redirect(url_for('results',q=q))

    Search = request.args['q'] # getting the text from the query
    cards = []

    q = MultifieldParser(["name", "desc"], schema=ix.schema)
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

def main():

    app.run() # run flask application

main()