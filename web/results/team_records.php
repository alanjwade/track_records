<?php

require_once(__DIR__ . '/../includes/track.php');
trackVisit();


// team_results.php

// Database connection
$db = new SQLite3('../data/track_records.sqlite');

// Get team_name and year from the request
$team_name = $_GET['team_name'];

// Fetch athletes for the given team and year
$sql = "SELECT 
            Events.name AS event_name,
            Athletes.name AS athlete_name,
            Teams.name AS team_name,
            strftime('%Y-%m-%d', Meets.meet_date),
            Meets.location,
            Meets.meet_date as meet_date,
            Results.result_orig AS result,
            MIN(Results.result_sort) AS result_sort
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Events ON Events.event_id = Results.event_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE Teams.name = :team_name
        GROUP BY event_name;
        ";

$stmt = $db->prepare($sql);
$stmt->bindValue(':team_name', $team_name, SQLITE3_TEXT);
$result = $stmt->execute();

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Records</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Team Records for <?php echo htmlspecialchars($team_name); ?></h1>
    <table>
        <thead>
            <tr>
                <th>Event Name</th>
                <th>Athlete Name</th>
                <th>Team Name</th>
                <th>Result</th>
                <th>Meet Date</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result->fetchArray(SQLITE3_ASSOC)): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['event_name']); ?></td>
                    <td><?php echo htmlspecialchars($row['athlete_name']); ?></td>
                    <td><?php echo htmlspecialchars($row['team_name']); ?></td>
                    <td><?php echo htmlspecialchars($row['result']); ?></td>
                    <td><?php echo htmlspecialchars($row['meet_date']); ?></td>
                </tr>
            <?php endwhile; ?>
        </tbody>
    </table>
</body>
<?php require_once '../includes/footer.php'; ?>
</html>