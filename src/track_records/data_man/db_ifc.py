from pprint import pprint as pp
import sqlite3
from pathlib import Path

def generate_new_db(db):

    pp("Creating db {}".format(db))
    try:
        Path(db).unlink()
    except:
        pass
    conn = sqlite3.connect(db)
    return conn

def get_db(db):
    pp("Opening db {}".format(db))

    conn = sqlite3.connect(db)
    return conn