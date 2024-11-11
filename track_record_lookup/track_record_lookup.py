from flask import Flask, render_template, request, current_app, g
import sqlite3
from pprint import pprint
import datetime

app = Flask(__name__)


def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val)


sqlite3.register_converter("date", convert_date)


def get_db_connection():
    conn = sqlite3.connect("/home/alan/Documents/track/records/track_records.db")
    conn.row_factory = sqlite3.Row
    return conn


#     if 'db' not in g:
#         g.db = sqlite3.connect("/home/alan/Documents/track/records/track_results.db")
# #        g.db.row_factory = sqlite3.Row
#     return g.db


@app.route("/")
def index():

    # Get a list of all the schools.

    conn = get_db_connection()

    query = """
        SELECT
            *
        FROM
            Teams
        WHERE
            conference_id = (SELECT
                                conference_id
                             FROM
                                Conferences
                             WHERE name = ?);
        """

    teams = conn.execute(query, ("NCIL",)).fetchall()
    query = """
        SELECT DISTINCT
            strftime('%Y', meet_date) AS year
        FROM
            Meets;
        """

    years = conn.execute(query).fetchall()

    for year in years:
        print(year["year"])

    #

    conn.close()

    return render_template("index.html", teams=teams, years=years)


@app.route("/results", methods=["POST"])
def results():
    school_name = request.form["team_name"]

    print(school_name)

    conn = get_db_connection()

    # Query to find school records
    query = """
        SELECT 
            Teams.name AS team_name,
            Events.full_name AS event_full_name,
            Athletes.name AS athlete_name,
            Meets.meet_date,
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
        GROUP BY event_full_name;
        """
    school_records = conn.execute(query, (school_name,)).fetchall()
    conn.close()

    for school_record in school_records:
        print(school_record.keys())
        # pprint(school_record)

    return render_template("results.html", school_records=school_records)


@app.route("/select_athlete", methods=["POST"])
def select_athlete():
    team_name = request.form["team_name"]
    year = request.form["year"]

    print(team_name)

    conn = get_db_connection()

    # Query to find school records
    query = """
        SELECT DISTINCT 
            a.name AS name
        FROM 
            Athletes a
            INNER JOIN Results r ON a.athlete_id = r.athlete_id
            INNER JOIN Teams t ON r.team_id = t.team_id
            INNER JOIN Meets m on m.meet_id = r.meet_id
        WHERE t.name = ?
            AND strftime('%Y', m.meet_date) = ?;
        """
    athletes = conn.execute(query, (team_name, year)).fetchall()
    conn.close()

    print(len(athletes))

    for athlete in athletes:
        print(athlete["name"])
        # pprint(school_record)

    return render_template(
        "select_athlete.html", athletes=athletes, team_name=team_name
    )


@app.route("/show_records", methods=["POST"])
def show_records():
    athlete_name = request.form["athlete_name"]
    team_name = request.form["team_name"]

    conn = get_db_connection()

    query = """
        SELECT 
            Teams.name AS team_name,
            Events.full_name AS event_full_name,
            Athletes.name AS athlete_name,
            Meets.meet_date,
            Meets.location,
            Results.result_orig AS result,
            MIN(Results.result_sort) AS result_sort
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Events ON Events.event_id = Results.event_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE   Teams.name = ?
            AND Athletes.name = ?
        GROUP BY
            Events.full_name;
        """

    records = conn.execute(query, (team_name, athlete_name)).fetchall()
    conn.close()

    for record in records:
        print(record["athlete_name"])
        print(record["event_full_name"])
        # pprint(school_record)

    return render_template("athlete_records.html", records=records)


if __name__ == "__main__":
    app.run(debug=True)
