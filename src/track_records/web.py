#!/var/www/track_records/venv/bin/python3

from flask import Flask, render_template, request, current_app, g
import sqlite3
from pprint import pprint
import datetime
from track_records.data_man import *

'''request structure:
index.html
    individual records
    pick team, go to indv_results_select_year.html

    team records
    pick team, go to results.html

    NCIL conference records
    go to conference_records.html

indv_results_select_year.html
    pick year, go to select_athlete.html

'''


app = Flask(__name__)
# app.template_folder = 'src/templates'

def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val)


sqlite3.register_converter("date", convert_date)


def get_db_connection():
    conn = sqlite3.connect("data/track_records.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


#     if 'db' not in g:
#         g.db = sqlite3.connect("/home/alan/Documents/track/records/track_results.db")
# #        g.db.row_factory = sqlite3.Row
#     return g.db


@app.route("/")
def index():
    conference_name = "NCIL"

    teams_raw = query_db("data/track_records.sqlite", q_all_teams_in_conference(), (conference_name,))
    teams = [team["team_name"] for team in teams_raw]
    years_raw = query_db("data/track_records.sqlite", q_years_records_are_available())
    years = [year["year"] for year in years_raw]

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


@app.route("/indv_results_select_athlete", methods=["POST"])
def indv_results_select_athlete():
    team_name = request.form["team_name"]
    year = request.form["year"]

    athletes_raw = query_db("data/track_records.sqlite", q_all_athletes_on_team_in_one_year(), (team_name, year))
    athletes = [athlete["athlete_name"] for athlete in athletes_raw]

    pprint(athletes_raw)
    pprint(athletes)

    return render_template(
        "indv_results_select_athlete.html", athletes=athletes, team_name=team_name
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
