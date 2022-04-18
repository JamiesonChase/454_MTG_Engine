import os
import json
from whoosh.index import *
from whoosh.fields import SchemaClass, TEXT, ID
from config import index_path, card_data

class CardSchema(SchemaClass):
    id        = ID(stored=True)
    name      = TEXT(stored=True)
    desc      = TEXT(stored=True)
    flavor    = TEXT(stored=True)
    url       = TEXT(stored=True)
    image_url = TEXT(stored=True)
    power     = TEXT(stored=True)
    toughness = TEXT(stored=True)
    rarity    = TEXT(stored=True)
    colors    = TEXT(stored=True)
    cost      = TEXT(stored=True)
    types     = TEXT(stored=True)


async def indexData():
    schema = CardSchema()

    # ensure index directory exists
    if not os.path.exists(index_path):
        os.mkdir(index_path)

    # if the index already exists, open and return it
    # delete contents of ./data/indexes after changes to force it to rebuild
    if exists_in(index_path):
        return open_dir(index_path)
    
    ix = create_in(index_path, schema)
    writer = ix.writer()

    with open(card_data, 'r') as f:
        data = json.load(f)

    for card in data:
        writer.add_document(
            name      = card['name'],
            id        = card['id'],
            desc      = card['desc'],
            flavor    = card['flavor'],
            url       = card['url'],
            image_url = card['image_url'],
            power     = card['power'],
            toughness = card['toughness'],
            rarity    = card['rarity'],
            colors    = card['colors'],
            cost      = card['cost'],
            types     = card['types']
        )

    writer.commit()
    return ix
