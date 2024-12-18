'''Just the SQL queries for different requests.'''


'''
The records for every event for one team.
The records for every event for the conference.
The records for one athlete.
The records for all athletes on a team.
The records for all athletes that were on the team in a particular year (ie, participated in a meet that year).
'''



def q_all_team_records(team_name):
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
    return query

    

def q_all_conference_records(conference_name):
    pass

def q_athlete_records(athlete_name):
    pass

def q_all_athletes_on_team_records(athlete_name, team_name):
    pass

def q_all_athletes_on_team_in_one_year_records(team_name, year):
    pass

