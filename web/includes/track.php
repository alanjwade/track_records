<?php
// Database configuration
$db_file = __DIR__ . '/../data/traffic.sqlite';
$db_dir = dirname($db_file);

try {
    $pdo = new PDO("sqlite:$db_file");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Check if directory is writable
        if (!is_writable($db_dir)) {
        throw new Exception("Directory '$db_dir' is not writable");
    }
 
    
    // Create visits table if it doesn't exist
    // SQLite uses INTEGER PRIMARY KEY instead of AUTO_INCREMENT
    $pdo->exec("CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY,
        ip_address TEXT,
        user_agent TEXT,
        page_url TEXT,
        visit_time DATETIME,
        referrer TEXT
    )");
} catch(PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}

// track.php - Add this at the top of pages you want to track
function trackVisit() {
    global $pdo;
    
    $ip = $_SERVER['REMOTE_ADDR'];
    $user_agent = $_SERVER['HTTP_USER_AGENT'];
    $page_url = $_SERVER['REQUEST_URI'];
    $referrer = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : '';
    
    $stmt = $pdo->prepare("INSERT INTO visits (ip_address, user_agent, page_url, visit_time, referrer) 
                          VALUES (?, ?, ?, datetime('now'), ?)");
    $stmt->execute([$ip, $user_agent, $page_url, $referrer]);
}

// stats.php - Display traffic statistics
function displayStats() {
    global $pdo;
    
    // Get today's visits - using SQLite date functions
    $stmt = $pdo->query("SELECT COUNT(*) FROM visits 
                        WHERE date(visit_time) = date('now')");
    $today_visits = $stmt->fetchColumn();
    
    // Get yesterday's visits
    $stmt = $pdo->query("SELECT COUNT(*) FROM visits 
                        WHERE date(visit_time) = date('now', '-1 day')");
    $yesterday_visits = $stmt->fetchColumn();
    
    // Get weekly visits for the last 8 weeks
    // SQLite doesn't have YEARWEEK(), so we'll use strftime for week grouping
    $stmt = $pdo->query("SELECT 
                            strftime('%W', visit_time) as week,
                            COUNT(*) as visits,
                            MIN(date(visit_time)) as week_start,
                            MAX(date(visit_time)) as week_end
                        FROM visits 
                        WHERE visit_time >= datetime('now', '-56 days')
                        GROUP BY strftime('%Y-%W', visit_time)
                        ORDER BY week_start DESC
                        LIMIT 8");
    $weekly_visits = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // Get popular pages
    $stmt = $pdo->query("SELECT page_url, COUNT(*) as count 
                        FROM visits 
                        GROUP BY page_url 
                        ORDER BY count DESC 
                        LIMIT 5");
    $popular_pages = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // Calculate percentage change
    $percent_change = $yesterday_visits > 0 
        ? round((($today_visits - $yesterday_visits) / $yesterday_visits) * 100, 1)
        : 0;
    
    ?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>Website Traffic Statistics</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .stats-container { max-width: 800px; margin: 0 auto; }
            .stat-box { 
                background: #f5f5f5;
                padding: 20px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .positive-change { color: green; }
            .negative-change { color: red; }
            .weekly-stats {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            .weekly-stats th, .weekly-stats td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            .weekly-stats tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <div class="stats-container">
            <h1>Website Traffic Statistics</h1>
            
            <div class="stat-box">
                <h2>Today's Visits: <?php echo $today_visits; ?></h2>
                <p>
                    Change from yesterday: 
                    <span class="<?php echo $percent_change >= 0 ? 'positive-change' : 'negative-change'; ?>">
                        <?php echo $percent_change; ?>%
                    </span>
                </p>
            </div>

            <div class="stat-box">
                <h2>Weekly Visits (Last 8 Weeks)</h2>
                <table class="weekly-stats">
                    <tr>
                        <th>Week Period</th>
                        <th>Total Visits</th>
                        <th>Daily Average</th>
                    </tr>
                    <?php foreach($weekly_visits as $week): ?>
                        <tr>
                            <td><?php echo date('M d', strtotime($week['week_start'])); ?> - 
                                <?php echo date('M d', strtotime($week['week_end'])); ?></td>
                            <td><?php echo $week['visits']; ?></td>
                            <td><?php echo round($week['visits'] / 7, 1); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </table>
            </div>
            
            <div class="stat-box">
                <h2>Most Visited Pages</h2>
                <ul>
                    <?php foreach($popular_pages as $page): ?>
                        <li>
                            <?php echo htmlspecialchars($page['page_url']); ?> 
                            (<?php echo $page['count']; ?> visits)
                        </li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>
    </body>
    </html>
    <?php
}
?>