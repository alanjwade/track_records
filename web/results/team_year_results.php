<?php

require_once(__DIR__ . '/../includes/track.php');
trackVisit();

// team_results.php

require_once('../includes/db_connect.php');

// Get team_name and year from the request
$team_name = $_GET['team_name'];
$year = $_GET['year'];

// Fetch meet dates for the given year
$meet_dates_sql = "SELECT DISTINCT strftime('%Y-%m-%d', meet_date) as meet_date
                   FROM Meets
                   WHERE strftime('%Y', meet_date) = :year";

$meet_dates_stmt = $db->prepare($meet_dates_sql);
$meet_dates_stmt->bindValue(':year', $year, SQLITE3_TEXT);
$meet_dates_result = $meet_dates_stmt->execute();

$meet_dates = [];
while ($row = $meet_dates_result->fetchArray(SQLITE3_ASSOC)) {
    $meet_dates[] = $row['meet_date'];
}
sort($meet_dates);

// For each meet_date, fetch the results for the given team

$team_results = [];

foreach ($meet_dates as $meet_date) {
    $results_sql = "SELECT
                        Results.result_orig AS result,
                        Athletes.name AS athlete_name,
                        Events.full_name AS event_name
                    FROM Results
                        INNER JOIN Teams ON Teams.team_id = Results.team_id
                        INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
                        INNER JOIN Events ON Events.event_id = Results.event_id
                        INNER JOIN Meets ON Meets.meet_id = Results.meet_id
                    WHERE Teams.name = :team_name AND strftime('%Y-%m-%d', Meets.meet_date) = :meet_date";

    $results_stmt = $db->prepare($results_sql);
    $results_stmt->bindValue(':team_name', $team_name, SQLITE3_TEXT);
    $results_stmt->bindValue(':meet_date', $meet_date, SQLITE3_TEXT);
    $results_result = $results_stmt->execute();

    $team_results[$meet_date] = [];
    while ($row = $results_result->fetchArray(SQLITE3_ASSOC)) {
        $team_results[$meet_date][] = [
            'athlete_name' => $row['athlete_name'],
            'event_name' => $row['event_name'],
            'result' => $row['result']
        ];
    }
}

// Sort each meet_date's results by athlete_name and then event_name
foreach ($team_results as $meet_date => $results) {
    usort($team_results[$meet_date], function($a, $b) {
        if ($a['athlete_name'] == $b['athlete_name']) {
            return strcmp($a['event_name'], $b['event_name']);
        }
        return strcmp($a['athlete_name'], $b['athlete_name']);
    });
}

$db->close();

// Render the results in an HTML table



?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Team Year Results</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Results for <?php echo htmlspecialchars($team_name); ?> in <?php echo htmlspecialchars($year); ?></h1>
    <table>
        <thead>
            <tr>
                <th>Athlete Name</th>
                <th>Event Name</th>
                <?php foreach ($meet_dates as $meet_date): ?>
                    <th><?php echo htmlspecialchars($meet_date); ?></th>
                <?php endforeach; ?>
            </tr>
        </thead>
        <tbody>
            <?php
            // Collect all athletes and events
            $athletes_events = [];
            foreach ($team_results as $results) {
                foreach ($results as $result) {
                    $athletes_events[$result['athlete_name']][$result['event_name']] = true;
                }
            }

            // Render rows
            foreach ($athletes_events as $athlete_name => $events) {
                foreach ($events as $event_name => $_) {
                    echo '<tr>';
                    echo '<td>' . htmlspecialchars($athlete_name) . '</td>';
                    echo '<td>' . htmlspecialchars($event_name) . '</td>';
                    foreach ($meet_dates as $meet_date) {
                        $result = '';
                        if (isset($team_results[$meet_date])) {
                            foreach ($team_results[$meet_date] as $res) {
                                if ($res['athlete_name'] == $athlete_name && $res['event_name'] == $event_name) {
                                    $result = htmlspecialchars($res['result']);
                                    break;
                                }
                            }
                        }
                        echo '<td>' . $result . '</td>';
                    }
                    echo '</tr>';
                }
            }
            ?>
        </tbody>
    </table>
</body>
<?php require_once '../includes/footer.php'; ?>
</html>