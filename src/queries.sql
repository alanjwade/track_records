--name: records_for_each_event_in_ncil_conference<>
SELECT 
    Events.name AS event_name,
    Athletes.name AS athlete_name,
    Meets.location,
    Results.result_orig AS result,
    Teams.name AS team_name,
    TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') as meet_date,
    Meets.location AS meet_location,
    Conferences.name AS conference_name,
    MIN(Results.result_sort) AS result_sort
FROM
    Results
    INNER JOIN Teams ON Teams.team_id = Results.team_id
    INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
    INNER JOIN Events ON Events.event_id = Results.event_id
    INNER JOIN Meets ON Meets.meet_id = Results.meet_id
    INNER JOIN Conferences ON Conferences.conference_id = Teams.conference_id
WHERE Conferences.name = 'NCIL'
GROUP BY event_name, Athletes.name, Events.name, Meets.location, Teams.name, Conferences.name, Results.result_orig, Meets.meet_date;

--name: get_all_teams<>

SELECT 
    Teams.name AS team_name
FROM 
    Teams;

--name: get_teams_and_athletes_on_team<>
SELECT 
    Teams.name AS team_name,
    Athletes.name AS athlete_name
FROM 
    Teams
INNER JOIN Athletes ON Athletes.team_id = Teams.team_id
ORDER BY 
    team_name, athlete_name;

--name: get_records_from_all_athletes_on_team<>_in_year<>
SELECT 
    Athletes.name AS athlete_name,
    Events.full_name AS event_name,
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
    athlete_name, event_name, Events.full_name, Meets.location;

--name: get_personal_records_for_one_athlete<>
SELECT 
    Athletes.name AS athlete_name,
    Events.full_name AS event_name,
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
WHERE 
    Teams.name = %s AND
    Athletes.name = %s
GROUP BY 
    event_name, Events.full_name, Meets.location;

--name: get_all_athletes_from_team_in_year<>

SELECT DISTINCT 
    Athletes.name AS athlete_name
FROM 
    Athletes
    INNER JOIN Results ON Athletes.athlete_id = Results.athlete_id
    INNER JOIN Teams ON Teams.team_id = Results.team_id
    INNER JOIN Meets ON Meets.meet_id = Results.meet_id
WHERE 
    Teams.name = %s AND 
    TO_CHAR(Meets.meet_date, 'YYYY') = %s;

--name: get_personal_records_for_athletes<>

SELECT 
    Athletes.name AS athlete_name,
    Events.full_name AS event_name,
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
WHERE 
    Athletes.name IN PLACEHOLDER1
    
GROUP BY 
    Athletes.name, Events.event_id, Events.full_name, Meets.location
HAVING 
    result_sort = MIN(result_sort);

--name: get_results_from_athletes<>

SELECT 
    Athletes.name AS athlete_name,
    Events.full_name AS event_name,
    TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') AS meet_date,
    Meets.location,
    Results.result_orig AS result,
    Results.result_sort
FROM 
    Results
    INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
    INNER JOIN Events ON Events.event_id = Results.event_id
    INNER JOIN Meets ON Meets.meet_id = Results.meet_id
    INNER JOIN Teams ON Teams.team_id = Results.team_id
WHERE 
    Athletes.name IN PLACEHOLDER1
    AND Teams.name = %s
ORDER BY 
    athlete_name, meet_date, event_name;

--name: get_prs_from_athletes_on_date<>

SELECT 
    Athletes.name AS athlete_name,
    Events.full_name AS event_name,
    TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') AS meet_date,
    Meets.location,
    Results.result_orig AS result,
    Results.result_sort
FROM 
    Results
    INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
    INNER JOIN Events ON Events.event_id = Results.event_id
    INNER JOIN Meets ON Meets.meet_id = Results.meet_id
    INNER JOIN Teams ON Teams.team_id = Results.team_id
WHERE 
    Athletes.name IN PLACEHOLDER1
    AND Teams.name = %s
    AND TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') = %s
    AND Results.result_sort = (
        SELECT MIN(r2.result_sort)
        FROM Results r2
        WHERE r2.athlete_id = Results.athlete_id
            AND r2.event_id = Results.event_id
    )
ORDER BY 
    athlete_name, event_name;

--name: get_top_5_places_from_team_on_date<>

SELECT 
    Athletes.name AS athlete_name,
    Events.full_name AS event_name,
    Results.result_orig AS result,
    Results.result_sort,
    Results.place
FROM 
    Results
    INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
    INNER JOIN Events ON Events.event_id = Results.event_id
    INNER JOIN Teams ON Teams.team_id = Results.team_id
    INNER JOIN Meets ON Meets.meet_id = Results.meet_id
WHERE 
    Teams.name = %s
    AND TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') = %s
    AND Results.place <= 5
ORDER BY 
    event_name, Results.place;

--name: get_top_8_athletes_per_event_for_team_in_year<>

WITH RankedResults AS (
    SELECT 
        Events.full_name AS event_name,
        Athletes.name AS athlete_name,
        MIN(Results.result_sort) AS best_result_sort,
        Results.result_orig AS result_orig,
        ROW_NUMBER() OVER (
            PARTITION BY Events.full_name 
            ORDER BY MIN(Results.result_sort)
        ) AS rank
    FROM 
        Results
        INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
        INNER JOIN Events ON Events.event_id = Results.event_id
        INNER JOIN Teams ON Teams.team_id = Results.team_id
        INNER JOIN Meets ON Meets.meet_id = Results.meet_id
    WHERE 
        Teams.name = %s
        AND TO_CHAR(Meets.meet_date, 'YYYY') = %s
    GROUP BY 
        Events.full_name, Athletes.name
)
SELECT 
    event_name,
    athlete_name,
    result_orig AS result,
    best_result_sort AS result_sort
FROM 
    RankedResults
WHERE
    rank <= 8
ORDER BY 
    event_name, best_result_sort;

--name: get_top_8_finishes_from_team_on_date<>

SELECT 
    Athletes.name AS athlete_name,
    Events.full_name AS event_name,
    Results.result_orig AS result,
    Results.result_sort,
    Results.place
FROM 
    Results
    INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
    INNER JOIN Events ON Events.event_id = Results.event_id
    INNER JOIN Teams ON Teams.team_id = Results.team_id
    INNER JOIN Meets ON Meets.meet_id = Results.meet_id
WHERE 
    Teams.name = %s
    AND TO_CHAR(Meets.meet_date, 'YYYY-MM-DD') = %s
    AND Results.place <= 8
ORDER BY 
    event_name, Results.place;