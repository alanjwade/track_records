
<?php

$dbPath = __DIR__ . '/../data/track_records.sqlite';

try {
    $db = new SQLite3($dbPath);
} catch (Exception $e) {
    die("Error connecting to database: " . $e->getMessage());
}
?>