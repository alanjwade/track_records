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
    create_db(conn)
    return conn

def get_db(db):
    pp("Opening db {}".format(db))

    conn = sqlite3.connect(db)
    return conn

def query_db(db, query, args=()):
    conn = get_db(db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def create_db(conn):

    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        """CREATE TABLE Athletes (
                    athlete_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    team_id INTEGER,
                    conference_id INTEGER,
                    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
                    FOREIGN KEY (conference_id) REFERENCES Conferences(conference_id)
                    );"""
    )

    cursor.execute(
        """CREATE TABLE Teams (
                    team_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    conference_id INTEGER,
                    FOREIGN KEY (conference_id) REFERENCES Conferences(conference_id)
                    );"""
    )

    cursor.execute(
        """CREATE TABLE Conferences (
                    conference_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                    );"""
    )

    cursor.execute(
        """CREATE TABLE Meets (
                    meet_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    meet_date DATE,
                    location TEXT
                    );"""
    )

    cursor.execute(
        """CREATE TABLE Events (
                    event_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL UNIQUE,
                    sort_order TEXT NOT NULL
                    );"""
    )

    cursor.execute(
        """CREATE TABLE Results (
                    result_id INTEGER PRIMARY KEY,
                    athlete_id INTEGER,
                    team_id INTEGER,
                    conference_id INTEGER,
                    meet_id INTEGER,
                    event_id INTEGER,
                    result_orig TEXT,
                    result_sort REAL,
                    place INTEGER,
                    FOREIGN KEY (athlete_id) REFERENCES Athletes(athlete_id),
                    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
                    FOREIGN KEY (conference_id) REFERENCES Teams(conference_id),
                    FOREIGN KEY (meet_id) REFERENCES Meets(meet_id),
                    FOREIGN KEY (event_id) REFERENCES Events(event_id)
                    );"""
    )
    #                    UNIQUE (athlete_id, meet_id, event_id)

    conn.commit()

    return conn

def execute_named_query(db_path, sql_file_path, query_name, params=None, PLACEHOLDER1=None):
    with open(sql_file_path, 'r') as file:
        content = file.read()
        # Match queries that start with --name: or /* @name */
        queries = {}
        
        # Match --name: style
        for query in content.split('--name:'):
            if query.strip():
                lines = query.split('\n')
                name = lines[0].strip()
                sql = '\n'.join(lines[1:]).strip()
                if sql:
                    queries[name] = sql

        if query_name not in queries:
            raise ValueError(f"Query '{query_name}' not found")
        
        if PLACEHOLDER1:
            for name, sql in queries.items():
                queries[name] = sql.replace('PLACEHOLDER1', PLACEHOLDER1)

        # print('------------------')
        # print (query_name)
        # print(len(queries))
        # print(queries[query_name])
                    
            
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()

            if params:
                cursor.execute(queries[query_name], params)
                rows = cursor.fetchall()
            else:
                cursor.execute(queries[query_name])
                rows = cursor.fetchall()
               
            result = [dict(row) for row in rows]

            return result