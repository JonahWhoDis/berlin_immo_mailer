import os
import json
import logging

#!/usr/bin/env python3

# Configure logging
logging.basicConfig(
    filename='deletion_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def remove_duplicate_entries(json_path):
    # Load the JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    seen_companies = set()
    deduped_entries = []
    duplicates_deleted = 0

    # Iterate through each entry
    for entry in entries:
        company = entry.get('companyName', '').strip()
        # If companyName exists and hasn't been seen, accept it.
        if company and company not in seen_companies:
            seen_companies.add(company)
            deduped_entries.append(entry)
        # If companyName is empty, just keep the entry (or you can modify this policy)
        elif not company:
            deduped_entries.append(entry)
        else:
            duplicates_deleted += 1
            logging.info(f"Deleted duplicate entry for company: {company}")

    return deduped_entries, duplicates_deleted

def main():
    json_input = 'website-monitor-app/websites.json'  # your JSON file with the list of entries
    json_output = 'website_results_deduplicated.json'  # file that will contain deduplicated entries

    deduped_entries, count = remove_duplicate_entries(json_input)
    
    # Write out the deduplicated JSON file
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(deduped_entries, f, ensure_ascii=False, indent=4)
    
    if count:
        print(f"Removed {count} duplicate entry(ies). New file created: {json_output}")
    else:
        print("No duplicates found.")

if __name__ == '__main__':
    main()