from pprint import pp
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
import sqlite3
import json
import re
from track_records.data_man.db_ifc import get_db, generate_new_db
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
import traceback
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

meet_arr = [
    {
        "meet_name": "2019_04_06 NCIL Meet #1",
        "url": "https://co.milesplit.com/meets/352832-ncil-2019-meet-1-2019/results",
        "page_content_file": "NCIL_2019_04_06.html",
        "date": "2019-04-06",
    },
    {
        "meet_name": "2022 NCIL Meet #2",
        "url": "https://co.milesplit.com/meets/456814-ncil-meet-2-2022/results",
        "page_content_file": "NCIL_2022_04_29.html",
        "date": "2022-04-29",
    },
    {
        "meet_name": "2022 NCIL Meet #3",
        "url": "https://co.milesplit.com/meets/456816-ncil-meet-3-2022/results",
        "page_content_file": "NCIL_2022_05_03.html",
        "date": "2022-05-03",
    },
    {
        "meet_name": "2022_05_06 NCIL Meet #4",
        "url": "https://co.milesplit.com/meets/456815-ncil-meet-4-2022/results",
        "page_content_file": "NCIL_2022_05_06.html",
        "date": "2022-05-06",
    },
    {
        "meet_name": "2022_05_10 NCIL Meet #5",
        "url": "https://co.milesplit.com/meets/460971-ncil-meet-5-2022/results",
        "page_content_file": "NCIL_2022_05_10.html",
        "date": "2022-05-10",
    },
    {
        "meet_name": "2022 NCIL Meet #6 League Championships",
        "url": "https://co.milesplit.com/meets/460973-ncil-meet-6-league-championships-2022/results/817291/formatted/",
        "page_content_file": "NCIL_2022_05_13.html",
        "date": "2022-05-13",
    },
    {
        "meet_name": "2023_04_12",
        "url": "https://co.milesplit.com/meets/525895-ncil-meet-1-2023/results/900625/formatted/",
        "page_content_file": "NCIL_2023_04_12.html",
        "date": "2023-04-12",
    },
    {
        "meet_name": "2023_04_19",
        "url": "https://co.milesplit.com/meets/534916-ncil-meet-2-2023/results/907237/formatted/",
        "page_content_file": "NCIL_2023_04_19.html",
        "date": "2023-04-19",
    },
    {
        "meet_name": "2023_04_26",
        "url": "https://co.milesplit.com/meets/534909-ncil-meet-3-2023/results/915434/formatted/",
        "page_content_file": "NCIL_2023_04_26.html",
        "date": "2023-04-26",
    },
    {
        "meet_name": "2023_05_04 NCIL Finals",
        "url": "https://co.milesplit.com/meets/520132-foothills-league-hs-ncil-ms-championships-2023/results/925348/formatted/",
        "page_content_file": "NCIL_2023_05_04.html",
        "date": "2023-05-04",
    },
    {
        "meet_name": "2024_04_22 NCIL #2",
        "url": "https://co.milesplit.com/meets/599765-ncil-meet-2-2024/results",
        "page_content_file": "NCIL_2024_04_22.html",
        "date": "2024-04-22",
    },
    {
        "meet_name": "2024_04_26 NCIL #3",
        "url": "https://co.milesplit.com/meets/599766-ncil-meet-3-2024/results",
        "page_content_file": "NCIL_2024_04_26.html",
        "date": "2024-04-26",
    },
    {
        "meet_name": "2024_05_04 NCIL #4",
        "url": "https://co.milesplit.com/meets/589497-foothills-league-championships-ncil-meet-4-2024/results",
        "page_content_file": "NCIL_2024_05_04.html",
        "date": "2024-05-04",
    },
    {
        "meet_name": "2024_05_10 NCIL Championship",
        "url": "https://co.milesplit.com/meets/599888-ncil-championship-2024/results",
        "page_content_file": "NCIL_2024_05_10.html",
        "date": "2024-05-10",
    },
    {
        "meet_name": "2025_04_05 NCIL #1",
        "url": "https://co.milesplit.com/meets/661391-ncil-meet-1-2025/results",
        "page_content_file": "NCIL_2025_04_05.html",
        "date": "2025-04-05",
    },
    {
        "meet_name": "2025_04_12 NCIL #2",
        "url": "https://ridgeviewclassical-my.sharepoint.com/:x:/g/personal/wgrace_ridgeviewclassical_org/EYa6dHQYsX5Pu1YX0OE38SMBEbuWvPguumTsEn-sjSTDyA?e=NdtGFp",
        "page_content_file": "NCIL_2_2025_04_12.xlsx",
        "date": "2025-04-12",
    },
    {
        "meet_name": "2025_04_26 NCIL #3",
        "url": "https://co.milesplit.com/meets/661390-ncil-meet-3-2025/results",
        "page_content_file": "NCIL_2025_04_26.html",
        "date": "2025-04-26",
    },
    {
        "meet_name": "2025_05_03 NCIL #4",
        "url": "https://co.milesplit.com/meets/663469-ncil-meet-4-2025/results",
        "page_content_file": "NCIL_2025_05_03.html",
        "date": "2025-05-03",
    },
    {
        "meet_name": "2025_05_10 NCIL Championship",
        "url": "https://co.milesplit.com/meets/661392-ncil-championship-2025/results",
        "page_content_file": "NCIL_2025_05_10.html",
        "date": "2025-05-10",
    },
]

taghash = {
    "m100m": {"name": "Boys 100 meter dash", "order": "asc"},
    "m200m": {"name": "Boys 200 meter dash", "order": "asc"},
    "m400m": {"name": "Boys 400 meter dash", "order": "asc"},
    "m800m": {"name": "Boys 800 meter run", "order": "asc"},
    "m1600m": {"name": "Boys 1600 meter run", "order": "asc"},
    "m110h": {"name": "Boys 110 meter high hurdles", "order": "asc"},
    "m200h": {"name": "Boys 200 meter hurdles", "order": "asc"},
    "m4x100m": {"name": "Boys 4x100 meter relay", "order": "asc"},
    "m4x200m": {"name": "Boys 4x200 meter relay", "order": "asc"},
    "m4x400m": {"name": "Boys 4x400 meter relay", "order": "asc"},
    "mhj": {"name": "Boys high jump", "order": "des"},
    "mlj": {"name": "Boys long jump", "order": "des"},
    "mtj": {"name": "Boys triple jump", "order": "des"},
    "md": {"name": "Boys discus", "order": "asc"},
    "ms": {"name": "Boys shot put", "order": "asc"},
    "f100m": {"name": "Girls 100 meter dash", "order": "asc"},
    "f200m": {"name": "Girls 200 meter dash", "order": "asc"},
    "f400m": {"name": "Girls 400 meter dash", "order": "asc"},
    "f800m": {"name": "Girls 800 meter run", "order": "asc"},
    "f1600m": {"name": "Girls 1600 meter run", "order": "asc"},
    "f100h": {"name": "Girls 100 meter high hurdles", "order": "asc"},
    "f200h": {"name": "Girls 200 meter hurdles", "order": "asc"},
    "f4x100m": {"name": "Girls 4x100 meter relay", "order": "asc"},
    "f4x200m": {"name": "Girls 4x200 meter relay", "order": "asc"},
    "f4x400m": {"name": "Girls 4x400 meter relay", "order": "asc"},
    "fhj": {"name": "Girls high jump", "order": "asc"},
    "flj": {"name": "Girls long jump", "order": "asc"},
    "ftj": {"name": "Girls triple jump", "order": "asc"},
    "fd": {"name": "Girls discus", "order": "asc"},
    "fs": {"name": "Girls shot put", "order": "asc"},
    "m3200": {"name": "Boys 3200 meter run", "order": "asc"},
    "f3200": {"name": "Girls 3200 meter run", "order": "asc"},
    "m4x800m": {"name": "Boys 4x800 meter relay", "order": "asc"},
    "f4x800m": {"name": "Girls 4x800 meter relay", "order": "asc"},
    "m300h": {"name": "Boys 300 meter hurdles", "order": "asc"},
    "f300h": {"name": "Girls 300 meter hurdles", "order": "asc"},
}


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()
sqlite3.register_adapter(datetime.date, adapt_date_iso)
def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val)
sqlite3.register_converter('date', convert_date)


def results_html_to_results_json():
    '''Convert all the results webpages into one json file.'''

    results = list()
    for meet in meet_arr:
        if meet['page_content_file'].endswith('.html'):
            results = results + parse_track_results(meet)
        elif meet['page_content_file'].endswith('.xlsx'):
            results = results + parse_excel_results(meet['page_content_file'], return_as_df=False, meet_info=meet)
            

    json_string = json.dumps(results, indent=4)

    with open("data/track_results.json", "w") as f:
        f.write(json_string)

    return True


def parse_track_results(one_meet):
    """
    This function parses track and field results from a single HTML page using Beautiful Soup.

    Args:
        url: The URL of the HTML page containing the results.

    Returns:
        A list of dictionaries, where each dictionary represents an athlete's result.
    """

    with open(Path("data/webpages", one_meet["page_content_file"]), "r") as f:
        print("parsing {}".format(one_meet["meet_name"]))
        content = f.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, "html.parser")

    # Find the header info
    header_info = soup.find("header", class_="meet")
    #print(header_info)

    venue_name = header_info.find("div", class_="venueName").text.strip()
    #print('venue:{}'.format(venue_name))

    # Find the table containing results (adjust selectors based on the website structure)
    results_table = soup.find(id="resultsList")  # Replace with appropriate class or id

    #    print(results_table)

    # If no table found, raise an error
    if not results_table:
        raise Exception("Results table not found")

    event_arr = soup.find_all("div", class_="eventResult")

    #   print(len(event_arr))

    results = []

    for event in event_arr:

        event_name = event.find(class_="eventName").text.strip()
        #        print("event name:{}".format(event_name))

        # print('***** event: {}'.format(event_name))
        event_tag = event.find("table")["id"]
        #        print("event tag:{}".format(event_tag))

        # Get the event column names
        event_cols_tmp = event.find("tr", class_="eventHeadRow").find_all("th")
        event_cols = [x.text.strip() for x in event_cols_tmp]

        # event_cols is now an array of column names
        # What ones are interesting? Just grab them all

        result_dict = {}
        # Extract data from table rows
        for row in event.find_all("tr")[1:]:  # Skip header row

            cells = row.find_all("td")

            result_dict = {}
            result_dict["venue"] = venue_name
            result_dict["event"] = event_tag
            result_dict["event_name"] = event_name
            result_dict["meet_name"] = one_meet["meet_name"]
            result_dict["meet_date"] = one_meet["date"]
            result_dict["school_abbr"] = None

            for index in range(0, len(event_cols)):
                result_dict[event_cols[index]] = cells[index].text.strip()
            # # Extract data based on cell positions (adjust based on website structure)
            # print('******** result: {}'.format(result_dict[event_cols[2]]))

            # rank = cells[0].text.strip()
            # name = cells[2].text.strip()
            # result = cells[5].text.strip()
            # # You can extract additional data like country, wind speed, etc. (adjust cell positions)

            # # Create a dictionary for each athlete's result
            # result_dict = {
            # "rank": rank,
            # "name": name,
            # "result": result,
            # }
            results.append(result_dict)
    #    pprint.pp(results)
    #    exit()

    return results

def get_page_content(one_meet):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)
    browser.get(one_meet["url"])

    content = browser.page_source

    with open(Path("webpages", one_meet["page_content_file"]), "w") as f:
        print("fetching {}".format(one_meet["meet_name"]))
        f.write(content)

    browser.quit()

    return True

def populate_db(dbfn):
    '''populate the database'''

    pp('Opening {}'.format(dbfn))
    conn = get_db(dbfn)
    with open("data/track_results.json", "r") as f:

        json_string = f.read()

        results = json.loads(json_string)
        print("Read track_results.json")

        insert_data(results, conn)

    conn.close()


def insert_data(results, conn):
    # List of keys from 'result' that are used in this function:
    # - "event_name"
    # - "event"
    # - "Team"
    # - "Athlete"
    # - "meet_name"
    # - "meet_date"
    # - "Mark"
    # - "venue"
    cursor = conn.cursor()

    for result in results:

        #      pp(result)

        event_name = result["event_name"]
        event_order = "asc"
        event_tag = result["event"]
        found = False

        # Find the normalized event in the taghash
        for norm_event in taghash.keys():
            #            print('{}:{}'.format(norm_event, event_tag))
            if norm_event in event_tag:
                event_name = norm_event
                event_order = taghash[norm_event]["order"]
                found = True
                break

        if found == False:
            if "m100h" in event_tag:
                event_name = "m110h"
                event_order = "asc"
            else:
                pp(result)
                exit()

        team_name = result["Team"]
        if "Athlete" in result.keys():
            athlete_name = result["Athlete"]
        else:
            athlete_name = team_name + " " + event_name + " relay team"

        event_full_name = taghash[event_name]['name']

        team_conference = conference(team_name)
        team_name = team_conference["team"]
        conference_name = team_conference["conf"]

        mark = result["Mark"]
        if "Place" in result.keys():
            place = result["Place"]
        meet_name = result["meet_name"]

        #        pp(event_name)

        conference_query = """INSERT OR IGNORE INTO Conferences (name) VALUES (?)"""
        cursor.execute(conference_query, (conference_name,))
        # Now the conference is in the DB

        conference_id_query = "SELECT conference_id FROM Conferences WHERE name = ?"
        cursor.execute(conference_id_query, (conference_name,))
        conference_id = cursor.fetchone()[0]  # Get conference ID from query result

        team_query = (
            """INSERT OR IGNORE INTO Teams (name, conference_id) VALUES (?, ?)"""
        )
        cursor.execute(team_query, (team_name, conference_id))
        # Now the team is in the DB

        team_id_query = "SELECT team_id FROM Teams WHERE name = ?"
        cursor.execute(team_id_query, (team_name,))
        team_id = cursor.fetchone()[0]  # Get team ID from query result

        athlete_query = """INSERT OR IGNORE INTO Athletes (name, team_id, conference_id) VALUES (?, ?, ?)"""
        cursor.execute(athlete_query, (athlete_name, team_id, conference_id))
        # Now the athlete is in the DB

        event_query = (
            """INSERT OR IGNORE INTO Events (name, full_name, sort_order) VALUES (?, ?, ?)"""
        )
        cursor.execute(event_query, (event_name, event_full_name, event_order))
        # Now the event is in the DB

        meet_query = """INSERT OR IGNORE INTO Meets (name, meet_date, location) VALUES (?, ?, ?)"""
        cursor.execute(
            meet_query,
            (
                meet_name,
                datetime.datetime.strptime(result["meet_date"], "%Y-%m-%d").date(),
                place,
            ),
        )
        # Now the meet is in the DB

        # Insert data (assuming IDs for teams, conferences, and events already exist)
        athlete_id_query = "SELECT athlete_id FROM Athletes WHERE name = ?"
        cursor.execute(athlete_id_query, (athlete_name,))
        athlete_id = cursor.fetchone()[0]  # Get athlete ID from query result

        event_id_query = "SELECT event_id FROM Events WHERE name = ?"
        cursor.execute(event_id_query, (event_name,))
        event_id = cursor.fetchone()[0]  # Get event ID from query result

        meet_id_query = "SELECT meet_id FROM Meets WHERE name = ?"
        cursor.execute(meet_id_query, (meet_name,))
        meet_id = cursor.fetchone()[0]  # Get meet ID from query result

        insert_result = """INSERT INTO Results (athlete_id,
                                                team_id, 
                                                conference_id, 
                                                meet_id, 
                                                event_id, 
                                                result_orig,
                                                result_sort,
                                                place)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

        if     mark.startswith('DISQ') \
            or mark.startswith('DQ') \
            or mark.startswith('DNF') \
            or mark.startswith('TMS') \
            or mark.startswith('NT'):
            mark_sort = 1000000
        elif "-" in mark:
            # it's a distance
            mark_sort = -1.0 * track_distance_to_float(mark)
        else:
            # it's time
            mark_sort = time_string_to_float(mark)

        try:
            cursor.execute(
                insert_result,
                (
                    athlete_id,
                    team_id,
                    conference_id,
                    meet_id,
                    event_id,
                    mark,
                    mark_sort,
                    place,
                ),
            )

        except Exception:
            print("Error:")
            pp(result)
            print(traceback.format_exc())
            exit()

    conn.commit()
def conference(school):
    conf_map = {
        "Ascent Classical Academy": {
            "team": "Ascent Classical Academy NOCO",
            "conf": "NCIL",
        },
        "Ascent Classical Academy Northern Colorado MS": {
            "team": "Ascent Classical Academy NOCO",
            "conf": "NCIL",
        },
        "Ascent Classical Academy of Northern Colorado": {
            "team": "Ascent Classical Academy NOCO",
            "conf": "NCIL",
        },
        "Dayspring Christian Academy": {
            "team": "Dayspring Christian Academy",
            "conf": "NCIL",
        },
        "Dayspring Christian Academy Middle School": {
            "team": 'Dayspring Christian Academy',
            "conf": "NCIL",
        },
        "Heritage Christian Academy": {
            "team": "Heritage Christian Academy",
            "conf": "NCIL",
        },
        "Heritage Christian Academy Middle School": {
            "team": "Heritage Christian Academy",
            "conf": "NCIL",
        },
        "Immanuel Lutheran Church": {
            "team": "Immanuel Lutheran Church",
            "conf": "NCIL",
        },
        "Loveland Classical Middle School": {
            "team": "Loveland Classical Middle School",
            "conf": "NCIL",
        },
        "Ridgeview Classical Schools": {
            "team": "Ridgeview Classical Schools",
            "conf": "NCIL",
        },
        "Saint Joseph Catholic School": {
            "team": "Saint Joseph Catholic School",
            "conf": "NCIL",
        },
        "St. John's Middle School": {
            "team": "St. John" "s Middle School",
            "conf": "NCIL",
        },
        "St Mary Catholic School": {"team": "St Mary Catholic School", "conf": "NCIL"},
        "West Ridge Academy": {"team": "West Ridge Academy", "conf": "NCIL"},
        "Windsor Charter Academy": {"team": "Windsor Charter Academy", "conf": "NCIL"},
        "Windsor Charter Academy Middle School": {
            "team": "Windsor Charter Academy",
            "conf": "NCIL",
        },
        "Jefferson Academy Middle School": {
            "team": "Jefferson Academy Middle School",
            "conf": "NCIL",
        },
        "Global Village Academy - North": {
            "team": "Global Village Academy - North",
            "conf": "NCIL",
        },
    }

    if school is None:
        # Return unique team names
        teams = set(item["team"] for item in conf_map.values())
        return sorted(list(teams))
    elif school in conf_map.keys():
        result = conf_map[school]
    else:
        result = {"team": school, "conf": "non-NCIL"}
    return result



def time_string_to_float(time_str):
    """
    Converts a string of the format 'h:mm:ss.ss', 'm:ss.ss' or 'ss.ss' to a float representing the total time in seconds.
    Returns None if time_str is empty or invalid format.

    Args:
        time_str: A string representing the time in hours, minutes and seconds format.

    Returns:
        A float representing the total time in seconds, or None if invalid input.
    """
    if not time_str or not isinstance(time_str, str):
        return None
        
    try:
        parts = time_str.split(":")
        if len(parts) == 3:  # h:mm:ss.ss format
            hours = parts[0].lstrip('0') or '0'
            minutes = parts[1].lstrip('0') or '0'
            seconds = parts[2]
        elif len(parts) == 2:  # mm:ss or mm:ss.ss format
            hours = "0"
            minutes = parts[0].lstrip('0') or '0'
            # Handle seconds with or without decimal point
            if "." in parts[1]:
                seconds = parts[1]
            else:
                seconds = parts[1].lstrip('0') or '0'
        else:  # ss.ss format
            hours = "0"
            minutes = "0" 
            seconds = time_str.lstrip('0') or '0'

        # Convert to floats
        hours = float(hours.strip())
        minutes = float(minutes.strip())
        seconds = float(seconds.strip())

        # Calculate total time in seconds
        return hours * 3600 + minutes * 60 + seconds

    except (ValueError, AttributeError):
        return None
def track_distance_to_float(td):
    """convert distances in the form of '85-11.25' to 85.90 or whatever that is."""

    
    try:
        feet, inches_str = td.split("-")
        if "." in inches_str:
            inches, fraction = inches_str.split(".")
        else:
            inches = inches_str
            fraction = "0"
    except Exception as e:
        print(f"Error parsing distance: '{td}'")
        raise

    # Convert each part to a float
    feet = float(feet.strip())
    inches = float(inches.strip())
    fraction = float(fraction) if fraction else 0
    # Convert inches and fraction to feet and add to total feet
    total_feet = (
        feet + inches / 12 + fraction / (12 * 100)
    )  # Account for potential hundredths in fraction

    return total_feet

def parse_excel_results(filename, return_as_df=True, meet_info=None):
    """Parse Excel spreadsheet with multiple sections per sheet into DataFrame.
    
    Args:
        filename (str): Excel file to parse
        
    Returns:
        pd.DataFrame: Normalized results DataFrame
    """
    xlsx = pd.read_excel(Path("data/spreadsheets", filename), sheet_name=None, header=None, dtype={'Time': str})
    results = []
    
    for sheet_name, df in xlsx.items():
        print(f"Parsing sheet: {sheet_name}")
        if df.empty:
            continue
            
        # Track current headers and section
        current_headers = []
        section_start = 0
        
        for idx, row in df.iterrows():
            # Check if this is a header row
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() == 'Event':
                # Save section start and get new headers
                section_start = idx
                current_headers = [str(h) for h in row.tolist() if pd.notna(h)]
                current_headers = [str(h) for h in row.tolist()[:20] if pd.notna(h)]
                continue

                
            # Skip empty rows
            if all(pd.isna(row)):
                continue
                
            # Skip if no headers set yet
            if not current_headers:
                continue
            # Skip if this is a header row
                
            # Get values and create Series with current headers
            values = row.tolist()[:len(current_headers)]
            row_data = pd.Series(values, index=current_headers)
            
            # if sheet_name == '400':
            #     pp('row: {}'.format(row_data))

            # Get event name and find matching tag
            event_name = str(row_data[current_headers[0]]).strip()
            event_tag = None
            
            for tag, info in taghash.items():
                if info['name'].lower() in event_name.lower():
                    event_tag = tag
                    break
                    
            if event_tag is None:
                continue


            # Process result based on available columns
            result_orig = None
            result_sort = None

            try:
                if 'Time' in current_headers:

                    if    str(row_data['Time']).startswith('DISQ') \
                        or str(row_data['Time']).startswith('DQ') \
                        or str(row_data['Time']).startswith('DNF') \
                        or str(row_data['Time']).startswith('TMS') \
                        or str(row_data['Time']).startswith('NT'):
                        result_orig = 'NT'
                        result_sort = 1000000
                    else:
                        result_orig = str(row_data['Time'])
                        if '.' in result_orig:
                            # Limit to 2 digits after the decimal point
                            parts = result_orig.split('.')
                            result_orig = parts[0] + '.' + parts[1][:2]
                        result_sort = time_string_to_float(result_orig)

                elif 'Distance Feet' in current_headers and 'Distance in' in current_headers:
                    if pd.notna(row_data['Distance Feet']) and str(row_data['Distance Feet']) in ['DNT', 'NH', 'DNJ']:
                        result_orig = str(row_data['Distance Feet'])
                        result_sort = 0
                    else:
                        feet = int(row_data['Distance Feet']) if pd.notna(row_data['Distance Feet']) else 0
                        inches = float(row_data['Distance in']) if pd.notna(row_data['Distance in']) else 0
                        result_orig = f"{feet}-{inches}"
                        result_sort = -1.0 * (feet + inches/12)
                elif 'Distance' in current_headers or 'Height' in current_headers:
                    field = 'Height' if 'Height' in current_headers else 'Distance'
                    if pd.notna(row_data[field]):
                        if str(row_data[field]) in ['DNT', 'NH', 'DNJ']:
                            result_orig = str(row_data[field])
                            result_sort = 0
                        else:
                            dist_str = str(row_data[field]).replace('"','').replace("'","-")
                            # If no inches specified (no hyphen), add "-0"
                            if "-" not in dist_str:
                                dist_str = dist_str + "-0"
                            if dist_str.endswith('-'):
                                dist_str = dist_str + '0'
                            result_orig = dist_str
                            result_sort = -1.0 * track_distance_to_float(dist_str)
            except Exception as e:
                print("Error processing result:")
                pp(row_data) 
                raise
                
            # Build athlete name
            if 'Fname' in current_headers and 'Lname' in current_headers:
                athlete_name = f"{row_data['Fname']} {row_data['Lname']}".strip()
            elif 'FName' in current_headers and 'LName' in current_headers:
                athlete_name = f"{row_data['FName']} {row_data['LName']}".strip()
            else:
                athlete_name = row_data.get('Athlete', '')

            team_mapping = {'HCAMS': 'Heritage Christian Academy',
                            'STJMS': "St. John's Middle School",
                            'SJSMS': 'Saint Joseph Catholic School',
                            'ILCMS': 'Immanuel Lutheran Church',
                            'DCAMS': 'Dayspring Christian Academy',
                            'JFAMS': 'Jefferson Academy Middle School',
                            'WCAMS': 'Windsor Charter Academy',
                            'SMCSM': 'St Mary Catholic School',
                            'RIDCS': 'Ridgeview Classical Schools',
                            'JFAMS': 'Jefferson Academy',
                            'SJE': 'St. John the Evangalist'}
            
            team_abbr = row_data.get('TeamID', '')
            try:
                team_full_name = team_mapping[team_abbr]

            except:
                team_full_name = 'Unknown'

                # track_records.sqlite3 to results mapping:
                # Events.name <=> result.event (event_tag, like 'm100m')
                # Events.full_name <=> result.event_name (full name, like 'mens 100m')
                # Atheletes.name <=> result.Athlete (athlete name)
                # Teams.name <=> result.Team (Saint Joseph Catholic School)
                # Teams.conference_id <=> don't have one here
                # Results.results_orig <=> result.result_orig (raw result)
                # Results.result_sort <=> result.result_sort (converted result)
                # Results.place <=> result.venue (place in event)

                # Items needed for json:
                # - "event_name"
                # - "event"
                # - "Team"
                # - "Athlete"
                # - "meet_name"
                # - "meet_date"
                # - "Mark"
                # - "venue"
                
            result = {
                'event': event_tag,
                'event_name': event_name,
                'gender': event_tag[0].lower(),  # Get first letter (m/f) of event name
                'Athlete': athlete_name,
                'school_abbr': team_abbr if pd.notna(team_abbr) else None,
                'Team': team_full_name,
                'Mark': result_orig,
                'result_orig': result_orig, 
                'result_sort': result_sort,
                'venue': 'Skyline High School',
                'meet_name': meet_info['meet_name'] if meet_info and 'meet_name' in meet_info else filename.split('.')[0],
                'meet_date': meet_info['date'] if meet_info and 'date' in meet_info else filename.split('.')[0],
            }
            
            results.append(result)
    if return_as_df:
        return pd.DataFrame(results)
    else:
        return results

def assign_places(df):
    """
    Adds 'place' and 'team_score' columns based on sorting results within each event.
    First place gets 10 points, followed by 8, 6, 4, 2, and 1.
    """
    # Initialize new columns
    df['place'] = 0
    df['team_score'] = 0
    
    # Point values for places 1-6
    point_values = {1: 8, 2: 6, 3: 4, 4: 2, 5: 1}
    
    # Group by event and sort within each group
    for event, group in df.groupby('event'):
        # Sort ascending or descending based on event type
        ascending = True
        # if group['result_sort'].iloc[0] < 0:  # Field events are stored as negative values
        #     ascending = False
            
        # Sort and assign places
        sorted_group = group.sort_values('result_sort', ascending=ascending)
        
        # Assign places and points
        for i, (idx, row) in enumerate(sorted_group.iterrows(), 1):
            df.at[idx, 'place'] = i
            if i <= 5:  # Only first 6 places get points
                df.at[idx, 'team_score'] = point_values[i]
                
    return df

def print_team_scores(df):
    """Print team total scores separated by gender and show point-scoring results, and save to Excel"""
    # Get unique teams
    teams = df['school_abbr'].dropna().replace('', pd.NA).dropna().unique()
    # Create mapping from abbreviations to full team names
    team_mapping = df[['school_abbr', 'Team']].drop_duplicates().set_index('school_abbr')['Team'].to_dict()
    # Add manual mapping for ILCMS
    team_mapping['ILCMS'] = 'Immanuel Lutheran'

    pp(team_mapping)

    # Create dictionaries to store team scores by gender
    boys_scores = {}
    girls_scores = {}
    
    # Lists to store data for Excel
    excel_data = []
    
    # Calculate totals for each team/gender
    for team in teams:
        # Boys scores
        boys_results = df[
            (df['school_abbr'] == team) & 
            (df['team_score'] > 0) &
            (df['gender'] == 'm')
        ]
        boys_total = boys_results['team_score'].sum()
        
        if boys_total > 0:
            boys_scores[team] = boys_total
            
        # Girls scores 
        girls_results = df[
            (df['school_abbr'] == team) & 
            (df['team_score'] > 0) &
            (df['gender'] == 'f')
        ]
        girls_total = girls_results['team_score'].sum()
        
        if girls_total > 0:
            girls_scores[team] = girls_total

    # Print boys results and add to Excel data
    print("\nBOYS TEAM SCORES:")
    for team, score in sorted(boys_scores.items(), key=lambda x: x[1], reverse=True):
        team_name = team_mapping.get(team, team)
        print(f"\n{team_name}: {score} points")
        
        # Get scoring results for this team
        team_results = df[
            (df['school_abbr'] == team) & 
            (df['team_score'] > 0) &
            (df['gender'] == 'm')
        ].sort_values('team_score', ascending=False)
        
        for _, result in team_results.iterrows():
            detail = f"  {result['event_name']}: {result['Athlete']} - {result['Mark']} ({result['team_score']} points)"
            print(detail)
            
            # Add to Excel data
            excel_data.append({
                'Gender': 'Boys',
                'Team': team_name,
                'Total Score': score,
                'Event': result['event_name'],
                'Athlete': result['Athlete'],
                'Mark': result['Mark'],
                'Points': result['team_score']
            })
        
    print("\nGIRLS TEAM SCORES:") 
    for team, score in sorted(girls_scores.items(), key=lambda x: x[1], reverse=True):
        team_name = team_mapping.get(team, team)
        print(f"\n{team_name}: {score} points")
        
        # Get scoring results for this team
        team_results = df[
            (df['school_abbr'] == team) & 
            (df['team_score'] > 0) &
            (df['gender'] == 'f')
        ].sort_values('team_score', ascending=False)
        
        for _, result in team_results.iterrows():
            detail = f"  {result['event_name']}: {result['Athlete']} - {result['Mark']} ({result['team_score']} points)"
            print(detail)
            
            # Add to Excel data
            excel_data.append({
                'Gender': 'Girls',
                'Team': team_name,
                'Total Score': score,
                'Event': result['event_name'],
                'Athlete': result['Athlete'],
                'Mark': result['Mark'],
                'Points': result['team_score']
            })

    # Create DataFrame and save to Excel
    excel_df = pd.DataFrame(excel_data)
    
    # Create Excel writer
    with pd.ExcelWriter('team_scores.xlsx') as writer:
        # Write summary sheet with team totals
        summary_data = []
        for team, score in sorted(boys_scores.items(), key=lambda x: x[1], reverse=True):
            summary_data.append({'Gender': 'Boys', 'Team': team_mapping.get(team, team), 'Total Score': score})
        for team, score in sorted(girls_scores.items(), key=lambda x: x[1], reverse=True):
            summary_data.append({'Gender': 'Girls', 'Team': team_mapping.get(team, team), 'Total Score': score})
        
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Team Totals', index=False)
        
        # Write detailed results
        excel_df.to_excel(writer, sheet_name='Detailed Results', index=False)


def create_results_pdf(df, output_filename='meet_results.pdf', highlight=None):
    """Create PDF of meet results using reportlab.
    If highlight is provided, highlight rows where Team matches highlight in yellow.
    If highlight == 'all', assign a color to each team and highlight accordingly.
    """
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    def header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawString(72, 750, 'NCIL Meet #2 2025_04_12')
        canvas.restoreState()

    doc = BaseDocTemplate(output_filename, pagesize=letter)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='header_template', frames=frame, onPage=header)
    doc.addPageTemplates([template])

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )

    # Prepare team color mapping if highlight == 'all'
    team_colors = {}
    if highlight == 'all':
        # Use a palette of distinguishable colors
        palette = [
            colors.yellow, colors.lightblue, colors.lightgreen, colors.lavender,
            colors.beige, colors.khaki, colors.lightcoral, colors.lightcyan,
            colors.lightpink, colors.lightgrey, colors.orange, colors.aquamarine,
            colors.wheat, colors.thistle, colors.mistyrose, colors.honeydew
        ]
        teams = sorted(df['Team'].dropna().unique())
        for i, team in enumerate(teams):
            team_colors[team] = palette[i % len(palette)]

    # First add team scores summary page
    elements.append(Paragraph("Team Scores Summary", header_style))

    # Calculate team scores by gender
    team_scores = {'Boys': {}, 'Girls': {}}
    for _, row in df[df['team_score'] > 0].iterrows():
        gender = 'Boys' if row['gender'] == 'm' else 'Girls'
        team = row['Team']
        if team not in team_scores[gender]:
            team_scores[gender][team] = 0
        team_scores[gender][team] += row['team_score']

    # Create tables for boys and girls team scores
    for gender in ['Boys', 'Girls']:
        elements.append(Paragraph(f"\n{gender} Team Scores", header_style))

        sorted_teams = sorted(team_scores[gender].items(), key=lambda x: x[1], reverse=True)
        data = [['Place', 'Team', 'Points']]
        row_styles = []

        for place, (team, score) in enumerate(sorted_teams, 1):
            data.append([str(place), team, str(int(score))])
            if highlight == 'all' and team in team_colors:
                row_styles.append(('BACKGROUND', (0, place), (-1, place), team_colors[team]))
            elif highlight is not None and highlight != 'all' and team == highlight:
                row_styles.append(('BACKGROUND', (0, place), (-1, place), colors.yellow))

        table = Table(data, colWidths=[50, 300, 100])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ] + row_styles)
        table.setStyle(style)
        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

    elements.append(PageBreak())

    # Group by event and gender for detailed results
    # Sort by gender first, then by event order as in taghash
    tag_order = {v['name']: i for i, v in enumerate(taghash.values())}
    # Prepare a list of (event_name, gender) tuples in desired order
    event_gender_order = sorted(
        df.groupby(['event_name', 'gender']).groups.keys(),
        key=lambda x: (
            x[1],  # gender first ('f' before 'm')
            tag_order.get(x[0], 9999)
        )
    )

    for event_name, gender in event_gender_order:
        group = df[(df['event_name'] == event_name) & (df['gender'] == gender)]
        header = Paragraph(f"{event_name}", header_style)
        elements.append(header)

        is_field = any(x in event_name.lower() for x in ['jump', 'shot put', 'discus'])
        result_header = 'Distance' if is_field else 'Time'

        data = [['Place', 'Athlete', 'Team', result_header, 'Points']]
        row_styles = []

        for i, (_, row) in enumerate(group.sort_values('place').iterrows(), 1):
            result = row['result_orig']
            if result and any(c.isdigit() for c in result):
                try:
                    time_val = time_string_to_float(result)
                    if time_val is not None:
                        minutes = int(time_val // 60)
                        seconds = time_val % 60
                        result = f"{minutes}:{seconds:05.2f}"
                except:
                    pass

            row_data = [
                str(int(row['place'])),
                row['Athlete'],
                row['Team'],
                result,
                str(int(row['team_score'])) if row['team_score'] > 0 else ''
            ]
            data.append(row_data)

            if highlight == 'all' and row['Team'] in team_colors:
                row_idx = i
                row_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), team_colors[row['Team']]))
            elif highlight is not None and highlight != 'all' and row['Team'] == highlight:
                row_idx = i
                row_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.yellow))

        table = Table(data, colWidths=[40, 200, 150, 70, 50])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),
        ] + row_styles)
        table.setStyle(style)

        elements.append(table)
        elements.append(PageBreak())

    doc.build(elements)


    def create_award_certificate_pdf(pr_table, name, output_filename='award_certificate.pdf', places_table=None):
        """
        Create an award certificate PDF in landscape mode.
        pr_table: list of dicts with keys ['event', 'mark', 'date']
        name: recipient's name (string)
        places_table: optional, list of dicts with keys ['event', 'mark', 'place']
        """

        doc = SimpleDocTemplate(
            output_filename,
            pagesize=landscape(letter),
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=48,
            alignment=TA_CENTER,
            spaceAfter=24,
            leading=54,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("Award Certificate", title_style))

        # Presented To
        presented_style = ParagraphStyle(
            'PresentedTo',
            parent=styles['Heading2'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=28,
            fontName='Helvetica'
        )
        elements.append(Paragraph("Presented To", presented_style))

        # Name
        name_style = ParagraphStyle(
            'Name',
            parent=styles['Heading1'],
            fontSize=36,
            alignment=TA_CENTER,
            spaceAfter=36,
            leading=40,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(name, name_style))

        # PR Table
        pr_data = [['Event', 'Mark', 'Date']]
        for rec in pr_table:
            pr_data.append([rec['event'], rec['mark'], rec['date']])
        pr_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 18),
            ('FONTSIZE', (0, 1), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ])
        pr_table_obj = Table(pr_data, colWidths=[220, 120, 120])
        pr_table_obj.setStyle(pr_table_style)
        elements.append(pr_table_obj)
        elements.append(Spacer(1, 24))

        # Places Table (optional)
        if places_table:
            places_data = [['Event', 'Mark', 'Place']]
            for rec in places_table:
                places_data.append([rec['event'], rec['mark'], str(rec['place'])])
            places_table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 18),
                ('FONTSIZE', (0, 1), (-1, -1), 16),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ])
            places_table_obj = Table(places_data, colWidths=[220, 120, 120])
            places_table_obj.setStyle(places_table_style)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Championship Places", styles['Heading2']))
            elements.append(places_table_obj)
            elements.append(Spacer(1, 24))

        # Footer with date and coach
        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 16)
            canvas.drawString(72, 36, "May 12th, 2025")
            canvas.drawRightString(doc.pagesize[0] - 72, 36, "Coach Alan Wade")
            canvas.restoreState()

        doc.build(elements, onFirstPage=footer, onLaterPages=footer)