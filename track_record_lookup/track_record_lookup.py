from flask import Flask, render_template, request, current_app, g
import sqlite3
from pprint import pprint

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("/home/alan/Documents/track/records/track_records.db")
    conn.row_factory = sqlite3.Row
    return conn
#     if 'db' not in g:
#         g.db = sqlite3.connect("/home/alan/Documents/track/records/track_results.db")
# #        g.db.row_factory = sqlite3.Row
#     return g.db

@app.route('/')
def index():
    # return "<p>Hello, World!</p>"
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    school_name = request.form['school_name']

    print(school_name)

    conn = get_db_connection()

    # Query to find school records
    query = """
        SELECT 
            Teams.name AS team_name,
            Events.name AS event_name,
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
        GROUP BY event_name;
        """
    school_records = conn.execute(query, (school_name,)).fetchall()
    conn.close()

    for school_record in school_records:
        print(school_record.keys())
        # pprint(school_record)

    return render_template('results.html', school_records=school_records)


    # query = """
    #     SELECT
    #         E.name AS event_name,
    #         A.name AS athlete_name,
    #         strftime('%Y-%m-%d', M.meet_date),
    #         M.location,
    #         R.result_orig AS result,
    #         MIN(R.result_sort) AS result_sort
    #     FROM
    #         Results R
    #         INNER JOIN Teams ON Teams.team_id = R.team_id
    #         INNER JOIN Athletes A ON A.athlete_id = R.athlete_id
    #         INNER JOIN Events E ON E.event_id = R.event_id
    #         INNER JOIN Meets M ON M.meet_id = R.meet_id
    #     WHERE 
    #         R.athlete_id IN (
    #             SELECT A.athlete_id
    #             FROM Results R
    #                 INNER JOIN Teams ON Teams.team_id = R.team_id
    #                 INNER JOIN Athletes A ON A.athlete_id = R.athlete_id
    #                 INNER JOIN Events E ON E.event_id = R.event_id
    #                 INNER JOIN Meets M ON M.meet_id = R.meet_id
    #             WHERE Teams.name = ? AND strftime('%Y', meet_date) = ?)
    #     GROUP BY athlete_name, event_name;
    #     """
    


    # cursor.execute("""
    #     SELECT t.name AS team_name, e.name AS event_name, MAX(r.result) AS school_record
    #     FROM Results r
    #     INNER JOIN Teams t ON r.team_id = t.team_id
    #     INNER JOIN Events e ON r.event_id = e.event_id
    #     WHERE t.name = ?
    #     GROUP BY t.name, e.name;
    # """, (school_name,))


if __name__ == '__main__':
    app.run(debug=True)