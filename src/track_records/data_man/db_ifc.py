from pprint import pprint as pp
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

def generate_new_db(db_params):
    pp(f"Creating db {db_params['dbname']}")
    # For PostgreSQL, you typically do not delete the DB file, but drop and recreate the database if needed.
    # This function assumes the database already exists and you have permissions to connect.
    conn = psycopg2.connect(**db_params)
    create_db(conn)
    return conn

def get_db(db_params):
    pp(f"Opening db {db_params['dbname']}")
    conn = psycopg2.connect(**db_params)
    return conn

def query_db(db_params, query, args=()):
    conn = get_db(db_params)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, args)
    rows = cur.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def create_db(conn):
    cursor = conn.cursor()
    # Create tables (PostgreSQL syntax)
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Athletes (
                    athlete_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    team_id INTEGER,
                    conference_id INTEGER,
                    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
                    FOREIGN KEY (conference_id) REFERENCES Conferences(conference_id)
                    );"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Teams (
                    team_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    conference_id INTEGER,
                    FOREIGN KEY (conference_id) REFERENCES Conferences(conference_id)
                    );"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Conferences (
                    conference_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                    );"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Meets (
                    meet_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    meet_date DATE,
                    location TEXT
                    );"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Events (
                    event_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL UNIQUE,
                    sort_order TEXT NOT NULL
                    );"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Results (
                    result_id SERIAL PRIMARY KEY,
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
    conn.commit()
    return conn

def execute_named_query(db_params, sql_file_path, query_name, params=None, PLACEHOLDER1=None):
    with open(sql_file_path, 'r') as file:
        content = file.read()
        queries = {}
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
        # Replace SQLite '?' placeholders with PostgreSQL '%s'
        query_sql = queries[query_name].replace('?', '%s')
        with psycopg2.connect(**db_params) as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            if params:
                cur.execute(query_sql, params)
                rows = cur.fetchall()
            else:
                cur.execute(query_sql)
                rows = cur.fetchall()
            result = [dict(row) for row in rows]
            return result