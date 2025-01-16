<?php

require_once(__DIR__ . '/includes/track.php');
trackVisit();

require_once 'includes/db_connect.php';
// No additional PHP code needed here

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
    <title>Individual Track Records</title>
</head>
<body>
    <h1>Individual Track Records</h1>
    <h2>Select team and the a year the athlete competed</h2>
    <form action="select/select_athlete.php" method="GET">
        <label for="team">Team:</label>
        <select name="team" id="team">
            <?php while ($row = $teams->fetchArray()): ?>
                <option value="<?php echo htmlspecialchars($row['team_name']); ?>"><?php echo htmlspecialchars($row['team_name']); ?></option>
            <?php endwhile; ?>
        </select>
        <br>
        <label for="year">Year competed:</label>
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
        <input type="submit" value="Go on to select athlete">
        <input type="submit" formaction="results/all_athlete_records.php" value="Go on to print records for all athletes on team">
    </form>
</body>
<h2>Select team to view team records:</h2>
<form action="results/team_records.php" method="GET">
    <label for="team_name">Team:</label>
    <select name="team_name" id="team_records">
        <?php
        // Reset the statement to fetch teams again
        $stmt->reset();
        $teams = $stmt->execute();
        while ($row = $teams->fetchArray()): ?>
            <option value="<?php echo htmlspecialchars($row['team_name']); ?>"><?php echo htmlspecialchars($row['team_name']); ?></option>
        <?php endwhile; ?>
    </select>
    <br>
    <input type="submit" value="View Team Records">
</form>
<head>
    <meta charset="UTF-8">
    <h1>NCIL Conference Records</h1>
</head>
<form action="results/conf_records.php" method="GET">
    <input type="hidden" name="conference_name" value="NCIL">
    <input type="submit" value="View NCIL Conference Records">
</form>
<hr>
<h1>Results</h1>
<h2>Show all results for a team for a particular year</h2>
<form action="results/team_year_results.php" method="GET">
    <label for="team_name">Team:</label>
    <select name="team_name" id="team_name">
        <?php
        // Reset the statement to fetch teams again
        $stmt->reset();
        $teams = $stmt->execute();
        while ($row = $teams->fetchArray()): ?>
            <option value="<?php echo htmlspecialchars($row['team_name']); ?>"><?php echo htmlspecialchars($row['team_name']); ?></option>
        <?php endwhile; ?>
    </select>
    <br>
    <label for="year">Year:</label>
    <select name="year" id="year">
        <?php 
        foreach ($years_array as $year): ?>
            <option value="<?php echo htmlspecialchars($year); ?>"><?php echo htmlspecialchars($year); ?></option>
        <?php endforeach; ?>
    </select>
    <br>
    <input type="submit" value="Show Results">
</form>

<?php require_once 'includes/footer.php'; ?>
</html>