from pprint import pp
import datetime
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
import sqlite3
import traceback
import json
import re
from track_records.data_man import *

# from requests_html import HTMLSession

def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()
sqlite3.register_adapter(datetime.date, adapt_date_iso)
def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val)
sqlite3.register_converter('date', convert_date)





def format_records(records):
    """print out formatted records"""

    for record in records:
        # pp(record)
        if len(record) > 3:
            print(
                "{:30.30s} {:30s} {:20s} {:20.20s} {:20s}".format(
                    record[1],
                    taghash[record[0]]["name"],
                    record[2],
                    record[3],
                    record[4],
                )
            )





def get_athletes_on_team(team_name, conn):
    """Given a text team_name, return a list of athlete_ids"""

    cursor = conn.cursor()

    team_id_query = "SELECT team_id FROM Teams WHERE name = ?"
    cursor.execute(team_id_query, (team_name,))
    team_id = cursor.fetchone()[0]  # Get team ID from query result

    print(team_id)

    athlete_id_query = "SELECT athlete_id FROM Athletes WHERE team_id = ?"
    cursor.execute(athlete_id_query, (team_id,))
    athlete_ids = cursor.fetchall()

    return athlete_ids


# def athlete_events(athlete_id, event_id):
#     '''Given the


def get_events_for_athlete_id(athlete_id, conn):
    """Given an athlete, return all event_ids they were in"""

    cursor = conn.cursor()

    event_id_query = "SELECT event_id FROM RESULTS WHERE athlete_id = ?"
    cursor.execute(event_id_query, (athlete_id,))
    event_ids = cursor.fetchall()

    return event_ids


def get_personal_records(athlete_id, conn):
    """Retrieves a list of events and personal records for a specific athlete.

    Args:
        athlete_id: The ID of the athlete to query results for.

    Returns:
        A list of dictionaries, where each dictionary contains 'event_name' and 'personal_record' keys.
    """

    # Connect to the database
    cursor = conn.cursor()

    # Query to find personal records grouped by event
    query = """
    SELECT e.name AS event_name, MIN(r.result) AS personal_record
    FROM Results r
    INNER JOIN Events e ON r.event_id = e.event_id
    WHERE r.athlete_id = ?
    GROUP BY e.name;
    """
    cursor.execute(query, (athlete_id,))

    # Fetch results and convert to list of dictionaries
    results = cursor.fetchall()
    personal_records = []
    for row in results:
        personal_records.append({"event_name": row[0], "personal_record": row[1]})

    conn.close()
    return personal_records


def get_team_id(school, conn):

    cursor = conn.cursor()

    query = """
    SELECT team_id
    FROM Teams
    Where name = ?;
    """

    cursor.execute(query, (school,))

    result = cursor.fetchone()[0]

    return result


def get_result_ids_from_team_id(team_id, conn):

    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    query = """
        SELECT result_id
        FROM Results
        WHERE team_id = ?;
        """
    cursor.execute(query, (team_id,))
    results = cursor.fetchall()
    conn.row_factory = None
    return results


def get_team_event_ids_from_results(team_id, conn):

    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT event_id
        FROM Results
        WHERE team_id = ?
        ORDER BY event_id ASC;
        """
    cursor.execute(query, (team_id,))
    results = cursor.fetchall()
    conn.row_factory = None
    return results


def get_prs_for_single_athlete_id(athlete_id, conn):

    cursor = conn.cursor()

    query = """
        SELECT
            E.name AS event_name,
            A.name AS athlete_name,
            strftime('%Y-%m-%d', M.meet_date),
            M.location,
            R.result_orig AS result,
            MIN(R.result_sort) AS result_sort
        FROM
            Results R
            INNER JOIN Athletes A ON A.athlete_id = R.athlete_id
            INNER JOIN Events E ON E.event_id = R.event_id
            INNER JOIN Meets M ON M.meet_id = R.meet_id
        WHERE R.athlete_id = ?
        GROUP BY E.name;
        """

    cursor.execute(query, (athlete_id,))

    results = cursor.fetchall()

    # pp(results)
    return results


def get_prs_for_athlete_ids(athlete_ids, conn):
    """athlete_ids is a list of athlete ids. Return a list of tuples."""
    cursor = conn.cursor()

    query = """
        SELECT
            E.name AS event_name,
            A.name AS athlete_name,
            strftime('%Y-%m-%d', M.meet_date),
            M.location,
            R.result_orig AS result,
            MIN(R.result_sort) AS result_sort
        FROM
            Results R
            INNER JOIN Athletes A ON A.athlete_id = R.athlete_id
            INNER JOIN Events E ON E.event_id = R.event_id
            INNER JOIN Meets M ON M.meet_id = R.meet_id
        WHERE R.athlete_id IN ({})
        GROUP BY E.name;
        """.format(
        ",".join("?" * len(athlete_ids))
    )

    cursor.execute(query, tuple(athlete_ids))

    results = cursor.fetchall()

    # pp(results)
    return results


def get_school_records(school, conn):
    """Return a list of events and the records for each from a particular school.
    The school is the text that should match what's in the 'Teams' table."""

    #    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    query = """
        SELECT 
            Events.name AS event_name,
            Athletes.name AS athlete_name,
            strftime('%Y-%m-%d', Meets.meet_date),
            Meets.location,
            Results.result_orig AS result,
            MIN(Results.result_sort) AS result_sort
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Events ON Events.event_id = Results.event_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE Teams.name = ?
        GROUP BY event_name;
        """
    cursor.execute(query, (school,))
    results = cursor.fetchall()
    return results


def get_prs_for_school(school, year, conn):
    """Find all participants in a school in a particular year. Then get their PRs."""

    cursor = conn.cursor()
    query = """
        SELECT
            Results.athlete_id AS athlete_id
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE
            Teams.name = ? AND strftime('%Y', meet_date) = ?;
        """

    cursor.execute(query, (school, year))
    results1 = cursor.fetchall()

    athlete_ids = list(set([x[0] for x in results1]))

    # results = get_prs_for_athlete_ids(athlete_ids, conn)

    # Now get PRs for each athlete in turn
    results = []
    for athlete_id in athlete_ids:
        prs = get_prs_for_single_athlete_id(athlete_id, conn)

        results = results + prs
        # pp(prs)
        # exit()
        # pp(athlete_id)
        # format_records(results)
        # exit()

    # pp(results)
    # exit()
    # format_records(results)
    return results


def get_prs_for_school2(school, year, conn):
    """Find all participants in a school in a particular year. Then get their PRs."""

    cursor = conn.cursor()
    query = """
        SELECT
            E.name AS event_name,
            A.name AS athlete_name,
            strftime('%Y-%m-%d', M.meet_date),
            M.location,
            R.result_orig AS result,
            MIN(R.result_sort) AS result_sort
        FROM
            Results R
            INNER JOIN Teams ON Teams.team_id = R.team_id
            INNER JOIN Athletes A ON A.athlete_id = R.athlete_id
            INNER JOIN Events E ON E.event_id = R.event_id
            INNER JOIN Meets M ON M.meet_id = R.meet_id
        WHERE 
            R.athlete_id IN (
                SELECT A.athlete_id
                FROM Results R
                    INNER JOIN Teams ON Teams.team_id = R.team_id
                    INNER JOIN Athletes A ON A.athlete_id = R.athlete_id
                    INNER JOIN Events E ON E.event_id = R.event_id
                    INNER JOIN Meets M ON M.meet_id = R.meet_id
                WHERE Teams.name = ? AND strftime('%Y', meet_date) = ?)
        GROUP BY athlete_name, event_name;
        """

    cursor.execute(query, (school, year))
    results = cursor.fetchall()

    return results




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch_web_pages", action="store_true")
    parser.add_argument("--generate_json", action="store_true")
    parser.add_argument("--generate_db", action="store_true")
    parser.add_argument("--query_db", action="store_true")
    parser.add_argument("--hack", action="store_true")
    parser.add_argument("--populate_db", action="store_true")
    parser.add_argument(
        "--db", default="data/track_records.sqlite"
    )
    args = parser.parse_args()


    if args.fetch_web_pages:
        for meet in meet_arr:
            get_page_content(meet)
        exit()

    if args.generate_json:

        results_html_to_results_json()

    if args.generate_db:

        results_json_to_results_db(args.db)

    if args.populate_db:
        populate_db(args.db)
        

    all_team_records = query_db(args.db, q_all_team_records(), ("Saint Joseph Catholic School",))
    pp(all_team_records)




if __name__ == "__main__":
    main()