import json
import os
import time
import random

# Load data from a JSON file
with open('cleaned.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# HTML template without input fields
html_template = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Initiativbewerbung</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}

        .page {{
            width: 210mm;
            min-height: 297mm;
            max-width: 210mm;
            max-height: 297mm;
            padding: 2mm 5mm;
            overflow: visible;
        }}

        .footer {{
            width: 210mm;
            font-size: 8pt;
            padding-top: 5mm;
        }}

        .footer-section {{
            width: 33%;
            text-align: left;
            vertical-align: top;
        }}

        .form-container {{
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="freier-bereich">
            <p id="letterContent">
                {formOfAddress},
                <br><br>
                ich hoffe, diese Nachricht erreicht Sie wohlauf. Mein Name ist {fullName} und ich bin auf der Suche nach einer Wohnung oder einem Zimmer in einer Wohngemeinschaft in Berlin. Da ich gehört habe, dass Ihre Immobilienverwaltung über ein vielfältiges Angebot an Mietobjekten verfügt, möchte ich mich hiermit initiativ bei Ihnen bewerben.
                <br><br>
                Für ein persönliches Gespräch stehe ich jederzeit zur Verfügung und freue mich auf Ihre Rückmeldung.
                <br><br>
                Mit freundlichen Grüßen,
                <br>
                {fullName}
            </p>
        </div>
    </div>
</body>
</html>
"""

def generate_html(entry):
    if entry['gender'] == 'male':
        form_of_address = f"Sehr geehrter Herr {entry['spokesperson']}"
    elif entry['gender'] == 'female':
        form_of_address = f"Sehr geehrte Frau {entry['spokesperson']}"
    else:
        form_of_address = f"Sehr geehrte Damen und Herren der {entry['companyName']}"

    # Populate the HTML template with the entry data
    html_content = html_template.format(
        formOfAddress=form_of_address,
    )

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
