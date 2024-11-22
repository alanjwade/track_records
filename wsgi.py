#!/var/www/track_records/venv/bin/python3
import sys
sys.path.insert(0, '/var/www/track_records/track_record_lookup')
sys.path.insert(0, '/var/www/track_records/venv/lib/python3.11/site-packages')
from track_record_lookup import app

application = app
