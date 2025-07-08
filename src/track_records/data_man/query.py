'''Just the SQL queries for different requests.'''


'''
The records for every event for one team.
The records for every event for the conference.
The records for one athlete.
The records for all athletes on a team.
The records for all athletes that were on the team in a particular year (ie, participated in a meet that year).
'''

# PostgreSQL uses DATE_TRUNC or TO_CHAR for date formatting, and uses SERIAL for autoincrementing IDs.
# Replace strftime('%Y-%m-%d', ...) with TO_CHAR(..., 'YYYY-MM-DD')
# Replace strftime('%Y', ...) with TO_CHAR(..., 'YYYY')

def q_all_team_records():
    query = """
        SELECT 
            Events.name AS event_name,
            Athletes.name AS athlete_name,
            TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') AS meet_date,
            Meets.location,
            Results.result_orig AS result,
            MIN(Results.result_sort) AS result_sort
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Events ON Events.event_id = Results.event_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE Teams.name = %s
        GROUP BY event_name, Athletes.name, Events.name, Meets.location
        ;
        """
    return query

    
def q_all_conference_records():
    query = """
        SELECT 
            Events.name AS event_name,
            Athletes.name AS athlete_name,
            TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') AS meet_date,
            Meets.location,
            Results.result_orig AS result,
            MIN(Results.result_sort) AS result_sort
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Events ON Events.event_id = Results.event_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
            INNER JOIN Conferences ON Conferences.conference_id = Teams.conference_id
        WHERE Conferences.name = %s
        GROUP BY event_name, Athletes.name, Events.name, Meets.location
        ;
        """
    return query

def q_athlete_records():
    query = """
        SELECT 
            Events.name AS event_name,
            TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') AS meet_date,
            Meets.location,
            Results.result_orig AS result,
            MIN(Results.result_sort) AS result_sort
        FROM
            Results
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Events ON Events.event_id = Results.event_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
            INNER JOIN Teams ON Teams.team_id = Results.team_id
        WHERE Athletes.name = %s
            AND Teams.name = %s
        GROUP BY event_name, Events.name, Meets.location
        ;
        """
    return query

def q_all_teams_in_conference():
    query = """
        SELECT 
            Teams.name AS team_name
        FROM
            Teams
            INNER JOIN Conferences ON Conferences.conference_id = Teams.conference_id
        WHERE Conferences.name = %s;
        """
    return query

def q_years_records_are_available():
    query = """
        SELECT DISTINCT TO_CHAR(Meets.meet_date, 'YYYY') AS year
        FROM Meets
        ORDER BY year DESC;
        """
    return query

def q_all_athletes_on_team_records():
    pass

def q_all_athletes_on_team_in_one_year_records():
    query = """
        SELECT 
            Athletes.name AS athlete_name,
            Events.name AS event_name,
            TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') AS meet_date,
            Meets.location,
            Results.result_orig AS result,
            MIN(Results.result_sort) AS result_sort
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Events ON Events.event_id = Results.event_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE 
            Teams.name = %s AND 
            Athletes.athlete_id IN (
                SELECT DISTINCT Athletes.athlete_id
                FROM Results
                INNER JOIN Meets ON Meets.meet_id = Results.meet_id
                INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
                WHERE TO_CHAR(Meets.meet_date, 'YYYY') = %s
            )
        GROUP BY 
            athlete_name, event_name, Events.name, Meets.location
        ;
        """
    return query

def q_all_athletes_on_team_in_one_year():
    query = """
        SELECT DISTINCT 
            Athletes.name AS athlete_name
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE 
            Teams.name = %s AND 
            TO_CHAR(Meets.meet_date, 'YYYY') = %s;
        """
    return query
