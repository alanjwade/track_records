<?php

require_once(__DIR__ . '/../includes/track.php');
trackVisit();

// results.php

require_once('../includes/db_connect.php');

// Get team_name and year from the request
$conference_name = $_GET['conference_name'];
$year = $_GET['year'];

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
            INNER JOIN Conferences ON Conferences.conference_id = Teams.conference_id
        WHERE Conferences.name = :conference_name
        GROUP BY event_name;
        ";

$stmt = $db->prepare($sql);
$stmt->bindValue(':conference_name', $conference_name, SQLITE3_TEXT);
$result = $stmt->execute();

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conference Records</title>
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
    <h1>Conference Records for <?php echo htmlspecialchars($conference_name); ?></h1>
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