<?php

require_once(__DIR__ . '/../includes/track.php');
trackVisit();
// results.php

require_once('../includes/db_connect.php');

// Get team_name and year from the request
$team_name = $_GET['team'];
$year = $_GET['year'];

// Fetch athletes for the given team and year
$sql = "SELECT 
            Athletes.name AS athlete_name,
            Events.full_name AS event_name,
            strftime('%Y-%m-%d', Meets.meet_date) AS meet_date,
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
            Teams.name = :team_name AND 
            Athletes.athlete_id IN (
                SELECT DISTINCT Athletes.athlete_id
                FROM Results
                INNER JOIN Meets ON Meets.meet_id = Results.meet_id
                INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
                WHERE strftime('%Y', Meets.meet_date) = :year
            )
        GROUP BY 
            athlete_name, event_name;";

$stmt = $db->prepare($sql);
$stmt->bindValue(':team_name', $team_name, SQLITE3_TEXT);
$stmt->bindValue(':year', $year, SQLITE3_TEXT);
$result = $stmt->execute();

?>

<!DOCTYPE html>
<html>
<head>
    <title>Athlete Results</title>
</head>
<body>
    <h1>Results for <?php echo htmlspecialchars($team_name); ?></h1>
    <table border="1">
        <tr>
        <th>Athlete</th>
        <th>Event Name</th>
        <th>Result</th>
        </tr>
        <?php while ($row = $result->fetchArray(SQLITE3_ASSOC)): ?>
            <tr>
            <td><?php echo htmlspecialchars($row['athlete_name']); ?></td>
            <td><?php echo htmlspecialchars($row['event_name']); ?></td>
            <td><?php echo htmlspecialchars($row['result']); ?></td>
            </tr>
        <?php endwhile; ?>
    </table>
</body>
<?php require_once '../includes/footer.php'; ?>
</html>