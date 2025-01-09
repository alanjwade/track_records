#!/var/www/track_records/.venv/bin/python3

import sys
import pip
sys.path.insert(0, '/var/www/track_records/src/track_records/')
sys.path.insert(0, '/var/www/track_records/.venv/lib/python3.11/site-packages')

from flask import Flask


#print(pip.get_installed_distributions())
from track_records import web_app

application = web_app
