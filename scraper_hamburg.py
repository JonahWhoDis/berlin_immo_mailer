import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

BASE_URL = "https://www.hamburg.de"
RESULTS_FILE = "results.json"

def load_existing_records():
    """Load existing results.json and return processed IDs and company names."""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                existing_ids = {entry["eintrag_id"] for entry in data if "eintrag_id" in entry}
                existing_names = {entry["companyName"].lower().strip() for entry in data if entry.get("companyName")}
                return existing_ids, existing_names, data
            except json.JSONDecodeError:
                print("Error decoding JSON file. Starting fresh.")
                return set(), set(), []
    return set(), set(), []

def extract_detail_info(detail_url, eintrag_id):
    """Extracts company information from the detail page."""
    try:
        response = requests.get(detail_url, timeout=50)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching detail page: {detail_url} - {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract JSON-LD data
    script = soup.find("script", type="application/ld+json")
    json_data = {}
    if script:
        try:
            json_data = json.loads(script.string.strip())
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON on: {detail_url} - {e}")

    # Extract company name
    company_name = json_data.get("name", "").strip()
    if not company_name:
        title_tag = soup.find("h1", id="title")
        if title_tag:
            company_name = title_tag.text.strip()

    telephone = json_data.get("telephone", "").strip()
    image = json_data.get("image", "").strip()

    # Extract Address
    address = ""
    for div in soup.find_all("div", class_="meta-box-main"):
        header = div.find("h3", class_="container-heading-sm")
        if header and "Adresse" in header.get_text():
            address_p = header.find_next_sibling("p")
            if address_p:
                address = " ".join(span.get_text(strip=True) for span in address_p.find_all("span"))
                break

    # Extract Zip Code & City
    zip_code, city = "", ""
    if address:
        match = re.search(r'(\d{5})\s*(.*)', address)
        if match:
            zip_code, city = match.groups()

    # Extract Email
    email = ""
    for div in soup.find_all("div", class_="meta-box-main"):
        header = div.find("h3", class_="container-heading-sm")
        if header and "E-Mail" in header.get_text():
            email_p = header.find_next_sibling("p")
            if email_p:
                email_link = email_p.find("a", href=True)
                if email_link and email_link["href"].startswith("mailto:"):
                    email = email_link["href"].replace("mailto:", "").strip()
                    break

    return {
        "eintrag_id": eintrag_id,
        "companyName": company_name,
        "spokesperson": "",
        "gender": "undefined",
        "email": email,
        "city": city,
        "zipCode": zip_code,
        "telephone": telephone,
        "image": image,
        "address": address,
        "url": detail_url
    }

def scrape_listings(start_page=0):
    """Scrapes all business listings and avoids duplicates."""
    processed_ids, processed_names, all_records = load_existing_records()
    current_page_url = f"{BASE_URL}/branchenbuch/hamburg/10233025/n{start_page}/"

    while current_page_url:
        '''        match = re.search(r'/n(\d+)/', current_page_url)
        if match and int(match.group(1)) > 63:
            break'''
        print(f"Fetching page: {current_page_url}")

        try:
            response = requests.get(current_page_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching page {current_page_url}: {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        detail_links = [a["href"] for a in soup.select("a.btn-details[href^='/branchenbuch/hamburg/eintrag/']")]

        # JSON-LD extraction if no direct links found
        if not detail_links:
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    json_data = json.loads(script.string.strip())
                    if "itemListElement" in json_data:
                        for item in json_data["itemListElement"]:
                            url = item.get("item", {}).get("url", "")
                            if url:
                                detail_links.append(url)
                except Exception:
                    pass

        print(f"Found {len(detail_links)} detail links.")

        for href in detail_links:
            href = BASE_URL + href if href.startswith("/") else href
            match = re.search(r'/eintrag/(\d+)', href)
            eintrag_id = match.group(1) if match else ""

            if not eintrag_id:
                continue

            record = extract_detail_info(href, eintrag_id)
            if not record:
                continue

            company_name_lower = record["companyName"].lower().strip()

            # Ensure skipping only when **both** eintrag_id and companyName match
            if eintrag_id in processed_ids and company_name_lower in processed_names:
                continue

            print(f"Processing new entry: {href}")
            all_records.append(record)
            processed_ids.add(eintrag_id)
            processed_names.add(company_name_lower)

            time.sleep(1)

        # Get next page
        next_page_anchor = soup.find("a", id="k-nav-next")
        current_page_url = BASE_URL + next_page_anchor["href"] if next_page_anchor else None

        if current_page_url:
            print(f"Next page found: {current_page_url}")
            time.sleep(2)

    return all_records

if __name__ == "__main__":
    results = scrape_listings()

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(results)} records.")
