import csv
from jinja2 import Environment, FileSystemLoader

# Load Jinja2 environment and templates directory
env = Environment(loader=FileSystemLoader('templates'))

# Paths to the CSV files for Adrienne Stewart, Alex Nemecek, and Amir Abston
adrienne_csv = "athletes/womens_team/Adrienne Stewart21142907.csv"
alex_csv = "athletes/mens_team/Alex Nemecek18820260.csv"
amir_csv = "athletes/mens_team/Amir Abston25395576.csv"

# Function to load and clean CSV data
def load_csv_data(file_path):
    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        data = [row for row in reader if row]  # Remove empty rows
    return data

# Extract athlete info from CSV
def extract_athlete_info(data):
    athlete_name = data[0][0] if len(data[0]) > 0 else "Unknown"
    athlete_id = data[1][0] if len(data) > 1 else "Unknown"
    athlete_link = f"https://www.athletic.net/athlete/{athlete_id}/cross-country/high-school"
    athlete_grade = next((row[2] for row in data if len(row) > 2 and row[2].isdigit()), "N/A")
    return athlete_name, athlete_id, athlete_link, athlete_grade

# Load CSV data for athletes
adrienne_data = load_csv_data(adrienne_csv)
alex_data = load_csv_data(alex_csv)
amir_data = load_csv_data(amir_csv)

# Extract athlete info
adrienne_name, adrienne_id, adrienne_link, adrienne_grade = extract_athlete_info(adrienne_data)
alex_name, alex_id, alex_link, alex_grade = extract_athlete_info(alex_data)
amir_name, amir_id, amir_link, amir_grade = extract_athlete_info(amir_data)

# Extract season records for each athlete
def extract_season_records(data):
    return [
        {"Year": int(row[1]), "Grade": int(row[2]), "Time": row[3]}
        for row in data if len(row) > 3 and row[1].isdigit() and int(row[1]) > 1999
    ]

# Extract season records
adrienne_records = extract_season_records(adrienne_data)
alex_records = extract_season_records(alex_data)
amir_records = extract_season_records(amir_data)

# Extract races from CSV data
def extract_races(data):
    races = []
    for row in data:
        # Skip rows that don't have enough data or are headers
        if len(row) < 6 or row[0] == "Name":
            continue
        if int(row[1]) < 1999:  # Assuming this is the year column
            race_dict = {
                "Place": row[1],
                "Time": row[3],
                "Date": row[4],
                "Meet": row[5]
            }
            races.append(race_dict)
    return races

# Filter 2024 races
def filter_2024_races(races):
    races_2024 = []
    for race in races:
        if "Aug" in race["Date"][0:3]:  # Example logic to filter races in 2024
            break
        races_2024.append(race)
    return races_2024

# Extract and filter races for each athlete
adrienne_races = extract_races(adrienne_data)
alex_races = extract_races(alex_data)
amir_races = extract_races(amir_data)

adrienne_races_2024 = filter_2024_races(adrienne_races)
alex_races_2024 = filter_2024_races(alex_races)
amir_races_2024 = filter_2024_races(amir_races)

# Generate dynamic HTML table for races
def races_table_maker(races_list):
    if not races_list:
        return "<p>No races available</p>"
    
    html_table = "<table>\n<tr>\n<th>Place</th>\n<th>Time</th>\n<th>Date</th>\n<th>Meet</th>\n</tr>\n"
    for race in races_list:
        html_table += f"<tr><td>{race['Place']}</td><td>{race['Time']}</td><td>{race['Date']}</td><td>{race['Meet']}</td></tr>\n"
    html_table += "</table>\n"
    return html_table

# Generate dynamic HTML table for season records
def table_maker(list_dicts):
    if not list_dicts:
        return "<p>No data available</p>"
    
    html_table = "<table>\n<tr>\n"
    for key in list_dicts[0].keys():
        html_table += f"<th>{key}</th>\n"
    html_table += "</tr>\n"
    
    for entry in list_dicts:
        html_table += "<tr>\n"
        for value in entry.values():
            html_table += f"<td>{value}</td>\n"
        html_table += "</tr>\n"
    
    html_table += "</table>\n"
    return html_table

# Generate tables for season records
adrienne_table = table_maker(adrienne_records)
alex_table = table_maker(alex_records)
amir_table = table_maker(amir_records)

# Generate tables for 2024 races
adrienne_races_table_2024 = races_table_maker(adrienne_races_2024)
alex_races_table_2024 = races_table_maker(alex_races_2024)
amir_races_table_2024 = races_table_maker(amir_races_2024)

# Top 10 for index page
mens_top10 = [{"Rank": 1, "Name": "Alex Nemecek", "Time": "19:21.4 SR"}, {"Rank": 2, "Name": "Amir Abston", "Time": "25:25.0 PR"}]
womens_top10 = [{"Rank": 1, "Name": "Adrienne Stewart", "Time": "23:31.1 SR"}]

mens_top10_table = table_maker(mens_top10)
womens_top10_table = table_maker(womens_top10)

# Render the index.html template (pass both top 10 lists)
index_template = env.get_template('index.html')
index_html = index_template.render(
    site_title="Men's and Women's Top 10 XC Times",
    page_heading="Top 10 Overall Rankings for Men and Women",
    mens_top10=mens_top10,  # Pass the raw data list
    womens_top10=womens_top10,  # Pass the raw data list
    mens_top10_table=mens_top10_table,
    womens_top10_table=womens_top10_table
)

# Save the generated index.html
with open("index.html", "w") as f:
    f.write(index_html)

# Render and save athlete pages
athlete_template = env.get_template('athlete.html')

# Adrienne Stewart's page
athlete_html_adrienne = athlete_template.render(
    athlete_name=adrienne_name,
    athlete_grade=adrienne_grade,
    athlete_school="Ann Arbor Skyline",
    season_year="2024",
    races_2024_table=adrienne_races_table_2024,  # Now passing the races table
    all_records_table=adrienne_table,
    season_notes="<li>2024: Best season performance</li>"
)
with open("athlete-adrienne.html", "w") as f:
    f.write(athlete_html_adrienne)

# Alex Nemecek's page
athlete_html_alex = athlete_template.render(
    athlete_name=alex_name,
    athlete_grade=alex_grade,
    athlete_school="Ann Arbor Skyline",
    season_year="2024",
    races_2024_table=alex_races_table_2024,  # Now passing the races table
    all_records_table=alex_table,
    season_notes="<li>2024: Best season performance</li>"
)
with open("athlete-alex.html", "w") as f:
    f.write(athlete_html_alex)

# Amir Abston's page
athlete_html_amir = athlete_template.render(
    athlete_name=amir_name,
    athlete_grade=amir_grade,
    athlete_school="Ann Arbor Skyline",
    season_year="2024",
    races_2024_table=amir_races_table_2024,  # Now passing the races table
    all_records_table=amir_table,
    season_notes="<li>2024: Best season performance</li>"
)
with open("athlete-amir.html", "w") as f:
    f.write(athlete_html_amir)

# Confirm completion
print('HTML pages generated for index, Adrienne Stewart, Alex Nemecek, and Amir Abston')
