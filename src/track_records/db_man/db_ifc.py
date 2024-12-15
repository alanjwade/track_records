from pprint import pprint as pp
import sqlite3
from pathlib import Path

def get_db(db):

    pp("Creating db {}".format(db))
    try:
        Path(db).unlink()
    except:
        pass
    conn = sqlite3.connect(db)


