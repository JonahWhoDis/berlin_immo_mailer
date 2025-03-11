import json
import os
import time
import random
from collections import defaultdict


# Load data from a JSON file
with open('results.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Your full Name
full_name = "Jonah Grosshanten"

# Title of the email
email_title = "Initiativbewerbung"

# Load the HTML template from a file
with open('template.html', 'r', encoding='utf-8') as file:
    html_template = file.read()

def generate_html(entry):
    if entry['gender'] == 'male':
        form_of_address = f"Sehr geehrter Herr {entry['spokesperson']}"
    elif entry['gender'] == 'female':
        form_of_address = f"Sehr geehrte Frau {entry['spokesperson']}"
    else:
        form_of_address = f"Sehr geehrte Damen und Herren der {entry['companyName']}"

    # Use defaultdict to prevent KeyError in case of missing placeholders
    html_content = html_template.format_map(defaultdict(str, {
        "formOfAddress": form_of_address,
        "fullName": full_name,
        "email_title": email_title
    }))

    # Define the filename based on the spokesperson's name
    filename = f"{entry['email'].replace(' ', '_')}.html"

    # Create the directory if it doesn't exist
    os.makedirs('output', exist_ok=True)

    # Write the HTML content to a file
    with open(os.path.join('output', filename), 'w', encoding='utf-8') as file:
        file.write(html_content)

# Process each entry in the JSON data
i = 0
for entry in data:
    i += 1
    generate_html(entry)
    print(f"Generated HTML for entry {i}: {entry['email']}")

print("HTML files generated successfully.")
