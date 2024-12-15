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

# from requests_html import HTMLSession

track_path = Path("/home/")
def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()
sqlite3.register_adapter(datetime.date, adapt_date_iso)
def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val)
sqlite3.register_converter('date', convert_date)

def parse_track_results(one_meet):
    """
    This function parses track and field results from a single HTML page using Beautiful Soup.

    Args:
        url: The URL of the HTML page containing the results.

    Returns:
        A list of dictionaries, where each dictionary represents an athlete's result.
    """

    with open(Path("webpages", one_meet["page_content_file"]), "r") as f:
        print("parsing {}".format(one_meet["meet_name"]))
        content = f.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, "html.parser")

    # Find the header info
    header_info = soup.find("header", class_="meet")

    venue_name = header_info.find("div", class_="venueName").text.strip()
    # print('venue:{}'.format(venue_name))

    # Find the table containing results (adjust selectors based on the website structure)
    results_table = soup.find(id="resultsList")  # Replace with appropriate class or id

    #    print(results_table)

    # If no table found, raise an error
    if not results_table:
        raise Exception("Results table not found")

    event_arr = soup.find_all("div", class_="eventResult")

    #   print(len(event_arr))

    results = []

    for event in event_arr:

        event_name = event.find(class_="eventName").text.strip()
        #        print("event name:{}".format(event_name))

        # print('***** event: {}'.format(event_name))
        event_tag = event.find("table")["id"]
        #        print("event tag:{}".format(event_tag))

        # Get the event column names
        event_cols_tmp = event.find("tr", class_="eventHeadRow").find_all("th")
        event_cols = [x.text.strip() for x in event_cols_tmp]

        # event_cols is now an array of column names
        # What ones are interesting? Just grab them all

        result_dict = {}
        # Extract data from table rows
        for row in event.find_all("tr")[1:]:  # Skip header row

            cells = row.find_all("td")

            result_dict = {}
            result_dict["venue"] = venue_name
            result_dict["event"] = event_tag
            result_dict["event_name"] = event_name
            result_dict["meet_name"] = one_meet["meet_name"]
            result_dict["meet_date"] = one_meet["date"]

            for index in range(0, len(event_cols)):
                result_dict[event_cols[index]] = cells[index].text.strip()
            # # Extract data based on cell positions (adjust based on website structure)
            # print('******** result: {}'.format(result_dict[event_cols[2]]))

            # rank = cells[0].text.strip()
            # name = cells[2].text.strip()
            # result = cells[5].text.strip()
            # # You can extract additional data like country, wind speed, etc. (adjust cell positions)

            # # Create a dictionary for each athlete's result
            # result_dict = {
            # "rank": rank,
            # "name": name,
            # "result": result,
            # }
            results.append(result_dict)
    #    pprint.pp(results)
    #    exit()

    return results


def get_page_content(one_meet):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)
    browser.get(one_meet["url"])

    content = browser.page_source

    with open(Path("webpages", one_meet["page_content_file"]), "w") as f:
        print("fetching {}".format(one_meet["meet_name"]))
        f.write(content)

    browser.quit()

    return True


meet_arr = [
    {
        "meet_name": "2019_04_06 NCIL Meet #1",
        "url": "https://co.milesplit.com/meets/352832-ncil-2019-meet-1-2019/results",
        "page_content_file": "NCIL_2019_04_06.html",
        "date": "2019-04-06",
    },
    {
        "meet_name": "2022 NCIL Meet #2",
        "url": "https://co.milesplit.com/meets/456814-ncil-meet-2-2022/results",
        "page_content_file": "NCIL_2022_04_29.html",
        "date": "2022-04-29",
    },
    {
        "meet_name": "2022 NCIL Meet #3",
        "url": "https://co.milesplit.com/meets/456816-ncil-meet-3-2022/results",
        "page_content_file": "NCIL_2022_05_03.html",
        "date": "2022-05-03",
    },
    {
        "meet_name": "2022_05_06 NCIL Meet #4",
        "url": "https://co.milesplit.com/meets/456815-ncil-meet-4-2022/results",
        "page_content_file": "NCIL_2022_05_06.html",
        "date": "2022-05-06",
    },
    {
        "meet_name": "2022_05_10 NCIL Meet #5",
        "url": "https://co.milesplit.com/meets/460971-ncil-meet-5-2022/results",
        "page_content_file": "NCIL_2022_05_10.html",
        "date": "2022-05-10",
    },
    {
        "meet_name": "2022 NCIL Meet #6 League Championships",
        "url": "https://co.milesplit.com/meets/460973-ncil-meet-6-league-championships-2022/results/817291/formatted/",
        "page_content_file": "NCIL_2022_05_13.html",
        "date": "2022-05-13",
    },
    {
        "meet_name": "2023_04_12",
        "url": "https://co.milesplit.com/meets/525895-ncil-meet-1-2023/results/900625/formatted/",
        "page_content_file": "NCIL_2023_04_12.html",
        "date": "2023-04-12",
    },
    {
        "meet_name": "2023_04_19",
        "url": "https://co.milesplit.com/meets/534916-ncil-meet-2-2023/results/907237/formatted/",
        "page_content_file": "NCIL_2023_04_19.html",
        "date": "2023-04-19",
    },
    {
        "meet_name": "2023_04_26",
        "url": "https://co.milesplit.com/meets/534909-ncil-meet-3-2023/results/915434/formatted/",
        "page_content_file": "NCIL_2023_04_26.html",
        "date": "2023-04-26",
    },
    {
        "meet_name": "2023_05_04 NCIL Finals",
        "url": "https://co.milesplit.com/meets/520132-foothills-league-hs-ncil-ms-championships-2023/results/925348/formatted/",
        "page_content_file": "NCIL_2023_05_04.html",
        "date": "2023-05-04",
    },
    {
        "meet_name": "2024_04_22 NCIL #2",
        "url": "https://co.milesplit.com/meets/599765-ncil-meet-2-2024/results",
        "page_content_file": "NCIL_2024_04_22.html",
        "date": "2024-04-22",
    },
    {
        "meet_name": "2024_04_26 NCIL #3",
        "url": "https://co.milesplit.com/meets/599766-ncil-meet-3-2024/results",
        "page_content_file": "NCIL_2024_04_26.html",
        "date": "2024-04-26",
    },
    {
        "meet_name": "2024_05_04 NCIL #4",
        "url": "https://co.milesplit.com/meets/589497-foothills-league-championships-ncil-meet-4-2024/results",
        "page_content_file": "NCIL_2024_05_04.html",
        "date": "2024-05-04",
    },
    {
        "meet_name": "2024_05_10 NCIL Championship",
        "url": "https://co.milesplit.com/meets/599888-ncil-championship-2024/results",
        "page_content_file": "NCIL_2024_05_10.html",
        "date": "2024-05-10",
    },
]

taghash = {
    "m100m": {"name": "Boys 100 meter dash", "order": "asc"},
    "m200m": {"name": "Boys 200 meter dash", "order": "asc"},
    "m400m": {"name": "Boys 400 meter dash", "order": "asc"},
    "m800m": {"name": "Boys 800 meter run", "order": "asc"},
    "m1600m": {"name": "Boys 1600 meter run", "order": "asc"},
    "m110h": {"name": "Boys 110 meter high hurdles", "order": "asc"},
    "m200h": {"name": "Boys 200 meter hurdles", "order": "asc"},
    "m4x100m": {"name": "Boys 4x100 meter relay", "order": "asc"},
    "m4x200m": {"name": "Boys 4x200 meter relay", "order": "asc"},
    "m4x400m": {"name": "Boys 4x400 meter relay", "order": "asc"},
    "mhj": {"name": "Boys high jump", "order": "des"},
    "mlj": {"name": "Boys long jump", "order": "des"},
    "mtj": {"name": "Boys triple jump", "order": "des"},
    "md": {"name": "Boys discus", "order": "asc"},
    "ms": {"name": "Boys shot put", "order": "asc"},
    "f100m": {"name": "Girls 100 meter dash", "order": "asc"},
    "f200m": {"name": "Girls 200 meter dash", "order": "asc"},
    "f400m": {"name": "Girls 400 meter dash", "order": "asc"},
    "f800m": {"name": "Girls 800 meter run", "order": "asc"},
    "f1600m": {"name": "Girls 1600 meter run", "order": "asc"},
    "f100h": {"name": "Girls 100 meter high hurdles", "order": "asc"},
    "f200h": {"name": "Girls 200 meter hurdles", "order": "asc"},
    "f4x100m": {"name": "Girls 4x100 meter relay", "order": "asc"},
    "f4x200m": {"name": "Girls 4x200 meter relay", "order": "asc"},
    "f4x400m": {"name": "Girls 4x400 meter relay", "order": "asc"},
    "fhj": {"name": "Girls high jump", "order": "asc"},
    "flj": {"name": "Girls long jump", "order": "asc"},
    "ftj": {"name": "Girls triple jump", "order": "asc"},
    "fd": {"name": "Girls discus", "order": "asc"},
    "fs": {"name": "Girls shot put", "order": "asc"},
    "m3200": {"name": "Boys 3200 meter run", "order": "asc"},
    "f3200": {"name": "Girls 3200 meter run", "order": "asc"},
    "m4x800m": {"name": "Boys 4x800 meter relay", "order": "asc"},
    "f4x800m": {"name": "Girls 4x800 meter relay", "order": "asc"},
    "m300h": {"name": "Boys 300 meter hurdles", "order": "asc"},
    "f300h": {"name": "Girls 300 meter hurdles", "order": "asc"},
}


# Print the results
# for result in results:
#     print(f"Rank: {result['rank']}, Name: {result['name']}, Result: {result['result']}")


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


def conference(school):
    conf_map = {
        "Ascent Classical Academy": {
            "team": "Ascent Classical Academy NOCO",
            "conf": "NCIL",
        },
        "Ascent Classical Academy Northern Colorado MS": {
            "team": "Ascent Classical Academy NOCO",
            "conf": "NCIL",
        },
        "Ascent Classical Academy of Northern Colorado": {
            "team": "Ascent Classical Academy NOCO",
            "conf": "NCIL",
        },
        "Dayspring Christian Academy": {
            "team": "Dayspring Christian Academy",
            "conf": "NCIL",
        },
        "Dayspring Christian Academy Middle School": {
            "team": 'Dayspring Christian Academy',
            "conf": "NCIL",
        },
        "Heritage Christian Academy": {
            "team": "Heritage Christian Academy",
            "conf": "NCIL",
        },
        "Heritage Christian Academy Middle School": {
            "team": "Heritage Christian Academy",
            "conf": "NCIL",
        },
        "Immanuel Lutheran Church": {
            "team": "Immanuel Lutheran Church",
            "conf": "NCIL",
        },
        "Loveland Classical Middle School": {
            "team": "Loveland Classical Middle School",
            "conf": "NCIL",
        },
        "Ridgeview Classical Schools": {
            "team": "Ridgeview Classical Schools",
            "conf": "NCIL",
        },
        "Saint Joseph Catholic School": {
            "team": "Saint Joseph Catholic School",
            "conf": "NCIL",
        },
        "St. John's Middle School": {
            "team": "St. John" "s Middle School",
            "conf": "NCIL",
        },
        "St Mary Catholic School": {"team": "St Mary Catholic School", "conf": "NCIL"},
        "West Ridge Academy": {"team": "West Ridge Academy", "conf": "NCIL"},
        "Windsor Charter Academy": {"team": "Windsor Charter Academy", "conf": "NCIL"},
        "Windsor Charter Academy Middle School": {
            "team": "Windsor Charter Academy",
            "conf": "NCIL",
        },
    }

    if school in conf_map.keys():
        result = conf_map[school]
    else:
        result = {"team": school, "conf": "non-NCIL"}
    return result


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


def insert_data(results, conn):

    cursor = conn.cursor()

    for result in results:

        #      pp(result)

        event_name = result["event_name"]
        event_order = "asc"
        event_tag = result["event"]
        found = False

        # Find the normalized event in the taghash
        for norm_event in taghash.keys():
            #            print('{}:{}'.format(norm_event, event_tag))
            if norm_event in event_tag:
                event_name = norm_event
                event_order = taghash[norm_event]["order"]
                found = True
                break

        if found == False:
            if "m100h" in event_tag:
                event_name = "m110h"
                event_order = "asc"
            else:
                pp(result)
                exit()

        team_name = result["Team"]
        if "Athlete" in result.keys():
            athlete_name = result["Athlete"]
        else:
            athlete_name = team_name + " " + event_name + " relay team"

        event_full_name = taghash[event_name]['name']

        team_conference = conference(team_name)
        team_name = team_conference["team"]
        conference_name = team_conference["conf"]

        mark = result["Mark"]
        place = result["venue"]
        meet_name = result["meet_name"]

        #        pp(event_name)

        conference_query = """INSERT OR IGNORE INTO Conferences (name) VALUES (?)"""
        cursor.execute(conference_query, (conference_name,))
        # Now the conference is in the DB

        conference_id_query = "SELECT conference_id FROM Conferences WHERE name = ?"
        cursor.execute(conference_id_query, (conference_name,))
        conference_id = cursor.fetchone()[0]  # Get conference ID from query result

        team_query = (
            """INSERT OR IGNORE INTO Teams (name, conference_id) VALUES (?, ?)"""
        )
        cursor.execute(team_query, (team_name, conference_id))
        # Now the team is in the DB

        team_id_query = "SELECT team_id FROM Teams WHERE name = ?"
        cursor.execute(team_id_query, (team_name,))
        team_id = cursor.fetchone()[0]  # Get team ID from query result

        athlete_query = """INSERT OR IGNORE INTO Athletes (name, team_id, conference_id) VALUES (?, ?, ?)"""
        cursor.execute(athlete_query, (athlete_name, team_id, conference_id))
        # Now the athlete is in the DB

        event_query = (
            """INSERT OR IGNORE INTO Events (name, full_name, sort_order) VALUES (?, ?, ?)"""
        )
        cursor.execute(event_query, (event_name, event_full_name, event_order))
        # Now the event is in the DB

        meet_query = """INSERT OR IGNORE INTO Meets (name, meet_date, location) VALUES (?, ?, ?)"""
        cursor.execute(
            meet_query,
            (
                meet_name,
                datetime.datetime.strptime(result["meet_date"], "%Y-%m-%d").date(),
                place,
            ),
        )
        # Now the meet is in the DB

        # Insert data (assuming IDs for teams, conferences, and events already exist)
        athlete_id_query = "SELECT athlete_id FROM Athletes WHERE name = ?"
        cursor.execute(athlete_id_query, (athlete_name,))
        athlete_id = cursor.fetchone()[0]  # Get athlete ID from query result

        event_id_query = "SELECT event_id FROM Events WHERE name = ?"
        cursor.execute(event_id_query, (event_name,))
        event_id = cursor.fetchone()[0]  # Get event ID from query result

        meet_id_query = "SELECT meet_id FROM Meets WHERE name = ?"
        cursor.execute(meet_id_query, (meet_name,))
        meet_id = cursor.fetchone()[0]  # Get meet ID from query result

        insert_result = """INSERT INTO Results (athlete_id,
                                                team_id, 
                                                conference_id, 
                                                meet_id, 
                                                event_id, 
                                                result_orig,
                                                result_sort,
                                                place)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

        if "-" in mark:
            # it's a distance
            mark_sort = -1.0 * track_distance_to_float(mark)
        else:
            # it's time
            mark_sort = time_string_to_float(mark)

        try:
            cursor.execute(
                insert_result,
                (
                    athlete_id,
                    team_id,
                    conference_id,
                    meet_id,
                    event_id,
                    mark,
                    mark_sort,
                    place,
                ),
            )

        except Exception:
            print("Error:")
            pp(result)
            print(traceback.format_exc())
            exit()

    conn.commit()


def track_distance_to_float(td):
    """convert distances in the form of '85-11.25' to 85.90 or whatever that is."""

    feet, inches_str = td.split("-")
    inches, fraction = inches_str.split(".")

    # Convert each part to a float
    feet = float(feet.strip())
    inches = float(inches.strip())
    fraction = float(fraction) if fraction else 0
    # Convert inches and fraction to feet and add to total feet
    total_feet = (
        feet + inches / 12 + fraction / (12 * 100)
    )  # Account for potential hundredths in fraction

    return total_feet


def time_string_to_float(time_str):
    """
    Converts a string of the format 'm:ss.ss' or 'ss.ss' to a float representing the total time in seconds.

    Args:
        time_str: A string representing the time in minutes and seconds format.

    Returns:
        A float representing the total time in seconds.

    Raises:
        ValueError: If the input string is not in the correct format.
    """
    try:
        # Split the string at the colon (':') if present
        if ":" in time_str:
            minutes, seconds = time_str.split(":")
        else:
            minutes = "0"
            seconds = time_str
    except ValueError:
        raise ValueError("Invalid time format. Please use 'm:ss.ss' or 'ss.ss'.")

    # Convert minutes and seconds to floats
    try:
        minutes = float(minutes.strip())
        seconds = float(seconds.strip())
    except ValueError:
        raise ValueError("Invalid time format. Please use 'm:ss.ss' or 'ss.ss'.")

    # Calculate total time in seconds
    total_seconds = minutes * 60 + seconds

    return total_seconds




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch_web_pages", action="store_true")
    parser.add_argument("--generate_json", action="store_true")
    parser.add_argument("--generate_db", action="store_true")
    parser.add_argument("--query_db", action="store_true")
    parser.add_argument("--hack", action="store_true")
    parser.add_argument("--populate_db", action="store_true")
    parser.add_argument(
        "--db", default="db/track_records.db"
    )
    args = parser.parse_args()

    if args.fetch_web_pages:
        for meet in meet_arr:
            get_page_content(meet)
        exit()

    if args.generate_json:

        results = list()
        for meet in meet_arr:
            results = results + parse_track_results(meet)

        json_string = json.dumps(results, indent=4)

        with open("track_results.json", "w") as f:
            f.write(json_string)

    if args.generate_db:

        #        pprint.pp(results)
        # exit()
        pp("Creating db {}".format(args.db))
        try:
            Path(args.db).unlink()
        except:
            pass
        conn = sqlite3.connect(args.db)
        create_db(conn)
    else:
        conn = sqlite3.connect(args.db)

    if args.populate_db:

        with open("track_results.json", "r") as f:
            json_string = f.read()

        results = json.loads(json_string)
        print("Read track_results.json")

        insert_data(results, conn)

    conn = sqlite3.connect(args.db)
    # athlete_ids = get_athletes_on_team("Saint Joseph Catholic School", conn)

    school_records = get_school_records('Saint Joseph Catholic School', conn)
    format_records(school_records)

    # school_prs = get_prs_for_school('Saint Joseph Catholic School', '2024', conn)
    # format_records(school_prs)

    # tables = conn.execute("SELECT sql FROM sqlite_schema WHERE name='Results';").fetchall()
    # print('test')
    # print(tables)
    # exit()
    # school_prs = get_prs_for_school2("Saint Joseph Catholic School", "2024", conn)
    # format_records(school_prs)

    # pp(athlete_ids)

    # event_ids = get_events_for_athlete_id(503, conn)

    # prs = get_personal_records(503, conn)

    # pp(prs)
    conn.close()

    if args.hack:

        with open("track_results.json", "r") as f:
            json_string = f.read()

        results = json.loads(json_string)
        print("Read track_results.json")

        for result in results:
            if result["Team"] == "Saint Joseph Catholic School":
                #            pprint.pp(result)
                if "Athlete" in result:
                    print(
                        "{:20} {:20} {:20} {:20}".format(
                            result["Athlete"],
                            result["event"],
                            result["Mark"],
                            result["meet_name"],
                        )
                    )

if __name__ == "__main__":
    main()