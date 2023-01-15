import sqlite3
from models.models import Card, Suit, Rank, get_value_of_card

# Crea la db base
with open('schema.sql') as file:
    script = file.read()

    con = sqlite3.connect('db.sqlite3')
    cur = con.cursor()

    cur.executescript(script)
    con.commit()

    # Inserta el mazo
    id = 1
    for suit in Suit:
        for rank in Rank:
            Card(id=id, suit=suit, rank=rank, value=get_value_of_card(rank, suit)).save()
            id += 1

    con.close()
