import os
import csv
import re
from jinja2 import Environment, FileSystemLoader

# Load Jinja2 environment and templates directory
env = Environment(loader=FileSystemLoader('templates'))

# Directories for men's and women's teams
mens_team_dir = "athletes/mens_team"
womens_team_dir = "athletes/womens_team"
output_dir = "athletes_html"

# Ensure the output directories exist
os.makedirs(f"{output_dir}/mens_team", exist_ok=True)
os.makedirs(f"{output_dir}/womens_team", exist_ok=True)

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
    
    # Find all valid grades and select the highest one
    grades = [int(row[2]) for row in data if len(row) > 2 and row[2].isdigit()]
    athlete_grade = max(grades, default="N/A")  # Get highest grade or "N/A" if no valid grades found
    
    try:
        with open(f"images/profiles/{athlete_id}.jpg", 'r') as file:
            athlete_photo = f"https://raw.githubusercontent.com/npisar/SI339-CPD3/refs/heads/main/images/profiles/{athlete_id}.jpg"
    except:
        athlete_photo = f"https://raw.githubusercontent.com/npisar/SI339-CPD3/refs/heads/main/images/default_image.jpg"

    return athlete_name, athlete_id, athlete_link, athlete_grade, athlete_photo

# Extract season records from CSV data
def extract_season_records(data):
    season_records = []
    for row in data:
        if len(row) > 3 and row[1].isdigit() and row[2].isdigit():
            season_record = {
                "Year": int(row[1]),
                "Grade": int(row[2]),
                "Time": row[3]
            }
            season_records.append(season_record)
    return season_records

# Extract races from CSV data
def extract_races(data):
    races = []
    for row in data:
        if len(row) < 6 or row[0] == "Name":
            continue
        
        try:
            if int(row[1]) < 1999:  # Assuming this is the year column
                race_dict = {
                    "Place": row[1],
                    "Time": row[3],
                    "Date": row[4],
                    "Meet": row[5],
                    "Name": row[0]  # Include the athlete's name here
                }
                races.append(race_dict)
        except ValueError:
            continue
    return races

# Filter 2024 races
# def filter_2024_races(races):
#     races_2024 = []
#     for race in races:
#         if "Jul" in race["Date"][0:3]:
#             break
#         races_2024.append(race)
#     return races_2024

# Generate dynamic HTML table for races
def races_table_maker(races_list):
    if not races_list:
        return "<p>No races available</p>"
    
    html_table = "<table>\n<tr>\n<th>Place</th>\n<th>Name</th>\n<th>Time</th>\n<th>Date</th>\n<th>Meet</th>\n</tr>\n"
    for race in races_list:
        html_table += f"<tr><td>{race['Place']}</td><td>{race['Name']}</td><td>{race['Time']}</td><td>{race['Date']}</td><td>{race['Meet']}</td></tr>\n"
    html_table += "</table>\n"
    return html_table

# Generate dynamic HTML table for 2024 races (excluding the Name column)
def races_table_maker_without_name(races_list):
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

# Process CSV files in a directory and generate HTML for each athlete
def process_team_csvs(team_dir, team_output_dir):
    for filename in os.listdir(team_dir):
        if filename.endswith(".csv"):
            file_path = os.path.join(team_dir, filename)
            data = load_csv_data(file_path)
            
            # Extract athlete info
            athlete_name, athlete_id, athlete_link, athlete_grade, athlete_photo = extract_athlete_info(data)
            if athlete_grade == "N/A":
                athlete_grade = "Athlete grade not found"
            else:
                athlete_grade = str(athlete_grade)
                athlete_grade += "th Grade"

            if len(athlete_name.split()) > 2:
                athlete_filename_raw = f"athlete-"
                for i in range(len(athlete_name.split())):
                    athlete_filename_raw += f"{athlete_name.split()[i].lower()}-"
                athlete_filename = athlete_filename_raw[:-1]
                # print(f"athlete_filename with longer than 2 index is {athlete_filename}!")
            else:
                athlete_filename = f"athlete-{(athlete_name.split()[0]+"-"+athlete_name.split()[1]).lower()}"
            # print(f"athlete_filename is {athlete_filename}")

            # Extract records and races
            athlete_records = extract_season_records(data)
            athlete_races = extract_races(data)
            # athlete_races_2024 = filter_2024_races(athlete_races)
            
            # Create tables for records and races
            athlete_table = table_maker(athlete_records)
            athlete_races_table = races_table_maker_without_name(athlete_races)
            
            # Render athlete's HTML
            athlete_template = env.get_template('athlete.html')
            athlete_html = athlete_template.render(
                athlete_name=athlete_name,
                athlete_filename = athlete_filename,
                athlete_grade=athlete_grade,
                athlete_photo=athlete_photo,
                athlete_id=athlete_id,
                athlete_link=athlete_link,
                athlete_school="Ann Arbor Skyline",
                season_year="2024",
                races_table=athlete_races_table,
                all_records_table=athlete_table,
                season_notes="<li>2024: Best season performance</li>"
            )
            
            # Save HTML file
            # print(f"athlete_name is {athlete_name}")
            # print(f"{athlete_name}'s grade is {athlete_grade}")
            output_path = os.path.join(team_output_dir, f"{athlete_filename}.html")
            with open(output_path, "w") as f:
                f.write(athlete_html)

# Call processing for both men's and women's teams
process_team_csvs(mens_team_dir, f"{output_dir}/mens_team")
process_team_csvs(womens_team_dir, f"{output_dir}/womens_team")

# Function to generate the top 10 fastest times
def generate_top_10(athletes_data):
    athlete_best_times = {}

    for data in athletes_data:
        races = extract_races(data)
        for race in races:
            athlete_name = race["Name"]
            time = race["Time"]

            # Clean the time to compare
            cleaned_time = clean_time(time)

            # Update the best time for the athlete
            if athlete_name not in athlete_best_times:
                athlete_best_times[athlete_name] = (cleaned_time, time)
            else:
                # Compare and keep the fastest time
                if cleaned_time < athlete_best_times[athlete_name][0]:
                    athlete_best_times[athlete_name] = (cleaned_time, time)

    # Create a list from the dictionary and sort it to get the top 10
    top_10 = sorted(athlete_best_times.items(), key=lambda x: x[1][0])[:10]

    # Format the top 10 for rendering
    return [{"Name": name, "Time": time[1]} for name, time in top_10]

def clean_time(time_str):
    clean_time_str = re.sub(r'[^\d:.]', '', time_str)
    time_parts = clean_time_str.split(':')

    if len(time_parts) == 2:
        minutes = int(time_parts[0])
        seconds = float(time_parts[1])
        return minutes * 60 + seconds
    else:
        return float(clean_time_str)

# Collect all data for top 10 tables
mens_top10 = generate_top_10([load_csv_data(os.path.join(mens_team_dir, f)) for f in os.listdir(mens_team_dir) if f.endswith(".csv")])
womens_top10 = generate_top_10([load_csv_data(os.path.join(womens_team_dir, f)) for f in os.listdir(womens_team_dir) if f.endswith(".csv")])

# Generate tables for the top 10
mens_top10_table = table_maker(mens_top10)
womens_top10_table = table_maker(womens_top10)

# Render the index.html template (pass both top 10 lists)
index_template = env.get_template('index.html')
index_html = index_template.render(
    site_title="Ann Arbor Skyline Top XC Times",
    page_heading_l1="Ann Arbor Skyline XC",
    page_heading_l2="Top 10 Men's and Women's Times",
    mens_top10=mens_top10,
    womens_top10=womens_top10,
    mens_top10_table=mens_top10_table,
    womens_top10_table=womens_top10_table
)

# Save the generated index.html
with open("index.html", "w") as f:
    f.write(index_html)

# Confirm completion
print(f'HTML pages generated for all athletes and index file.\n-------------\n\n')