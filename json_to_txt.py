import json

# Input and output file names
input_file = "website_list_without_dups.json"
output_file = "website_urls.txt"

# Read the JSON file
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Open the output file for writing
with open(output_file, "w", encoding="utf-8") as f:
    f.write("Enter one URL per line, and optionally add tags for each URL after a space, delineated by comma (,):\n")
    
    for entry in data:
        website = entry.get("website")
        company_name = entry.get("companyName", "").strip()
        tags = company_name if company_name else ""
        
        if website:
            f.write(f"{website} {tags}\n")

print(f"File '{output_file}' has been created successfully!")