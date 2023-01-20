import os
import tempfile
import pytest

from models.models import Card, Suit, Rank, get_value_of_card, get_connection


@pytest.fixture(autouse=True)
def database():
    _, file_name = tempfile.mkstemp()
    os.environ['TEST_DB'] = file_name

    # Crea la db de prueba
    with open('schema.sql') as file:
        script = file.read()

        con = get_connection()
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

    yield
    os.unlink(file_name)