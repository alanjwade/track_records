<?php
// results.php

// Database connection
$db = new SQLite3('data/track_records.sqlite');

// Get team_name and year from the request
$team_name = $_GET['team'];
$year = $_GET['year'];

// Fetch athletes for the given team and year
$sql = "SELECT DISTINCT 
            Athletes.name AS athlete_name
        FROM
            Results
            INNER JOIN Teams ON Teams.team_id = Results.team_id
            INNER JOIN Athletes ON Athletes.athlete_id = Results.athlete_id
            INNER JOIN Meets ON Meets.meet_id = Results.meet_id
        WHERE 
            Teams.name = :team_name AND 
            strftime('%Y', Meets.meet_date) = :year;
        ";

$stmt = $db->prepare($sql);
$stmt->bindValue(':team_name', $team_name, SQLITE3_TEXT);
$stmt->bindValue(':year', $year, SQLITE3_TEXT);
$result = $stmt->execute();

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Athletes</title>
</head>
<body>
    <h1>Select Athletes for <?php echo htmlspecialchars($team_name); ?> in <?php echo htmlspecialchars($year); ?></h1>
    <form action="athlete_results.php" method="GET">
        <input type="hidden" name="team_name" value="<?php echo htmlspecialchars($team_name); ?>">
        <input type="hidden" name="year" value="<?php echo htmlspecialchars($year); ?>">
        <div>
            <select name="athlete_name">
                <?php while ($row = $result->fetchArray(SQLITE3_ASSOC)): ?>
                    <option value="<?php echo htmlspecialchars($row['athlete_name']); ?>"><?php echo htmlspecialchars($row['athlete_name']); ?></option>
                <?php endwhile; ?>
            </select>
        </div>
        <button type="submit">Submit</button>
    </form>
</body>
</html>

<?php
$db->close();
?>
