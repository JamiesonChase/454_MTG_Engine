import os
import json
from whoosh.index import *
from whoosh.fields import SchemaClass, TEXT, ID
from config import index_path, card_data

class CardSchema(SchemaClass):
    id        = ID
    name      = TEXT(stored=True)
    desc      = TEXT(stored=True)
    url       = TEXT(stored=True)
    image_url = TEXT(stored=True)


def indexData():
    schema = CardSchema()

    # create empty index directory
    if not os.path.exists(index_path):
        os.mkdir(index_path)

    if exists_in(index_path):
        return open_dir(index_path)
    
    ix = create_in(index_path, schema)
    writer = ix.writer()

    with open(card_data) as f:
        data = json.load(f)
    for card in data:
        writer.add_document(name      = card['name'],
                            id        = card['id'],
                            desc      = card['desc'],
                            url       = card['url'],
                            image_url = card['image_url'])
    writer.commit()
    return ix