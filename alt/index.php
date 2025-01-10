<?php
// index.php
$db = new SQLite3('data/track_records.sqlite');

// Prepare the SQL statement with a placeholder for the conference name
$stmt = $db->prepare("
    SELECT Teams.name AS team_name
    FROM Teams
    INNER JOIN Conferences ON Conferences.conference_id = Teams.conference_id
    WHERE Conferences.name = :conference_name
");

// Bind the parameter to the placeholder
$conference_name = "NCIL";
$stmt->bindValue(':conference_name', $conference_name, SQLITE3_TEXT);
// $stmt->bindValue(1, $conference_name);

// Execute the prepared statement
$teams = $stmt->execute();

$years = $db->query("SELECT DISTINCT strftime('%Y', Meets.meet_date) AS year FROM Meets");
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Track Records</title>
</head>
<body>
    <h1>Select Team and Year</h1>
    <form action="select_athlete.php" method="GET">
        <label for="team">Team:</label>
        <select name="team" id="team">
            <?php while ($row = $teams->fetchArray()): ?>
                <option value="<?php echo htmlspecialchars($row['team_name']); ?>"><?php echo htmlspecialchars($row['team_name']); ?></option>
            <?php endwhile; ?>
        </select>
        <br>
        <label for="year">Year:</label>
        <select name="year" id="year">
            <?php 
            $years_array = [];
            while ($row = $years->fetchArray()) {
            $years_array[] = $row['year'];
            }
            rsort($years_array);
            foreach ($years_array as $year): ?>
            <option value="<?php echo htmlspecialchars($year); ?>"><?php echo htmlspecialchars($year); ?></option>
            <?php endforeach; ?>
        </select>
        <br>
        <input type="submit" value="Submit">
    </form>
</body>
</html>