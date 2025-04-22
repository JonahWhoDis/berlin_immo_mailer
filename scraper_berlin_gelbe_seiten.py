import time
import json
import os
import base64
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm  # Used for progress bars

# Set up logging to include the timestamp.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Save the results to a JSON file.
RESULTS_FILE = "gelbeseiten_results_verwaltung_neu.json"
# Base URL for the listings of real estate companies in Berlin.
BASE_URL = "https://www.gelbeseiten.de/branchen/immobilienverwaltung/berlin"

def load_page(driver, url):
    """Loads the specified URL and waits for the page to settle."""
    logging.info(f"Loading page: {url}")
    driver.get(url)
    # Pause briefly to let JavaScript load.
    time.sleep(3)
    logging.info("Page loaded successfully.")

def click_load_more(driver):
    """
    Looks for and clicks the "Mehr Anzeigen" button.
    Returns True if the button was clicked, False otherwise.
    """
    try:
        # Wait up to 5 seconds for the button to be clickable.
        load_more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "mod-LoadMore--button"))
        )
        load_more_button.click()
        logging.info("Clicked 'Mehr Anzeigen' button. Waiting for new listings...")
        time.sleep(2)  # Allow time for new listings to load.
        return True
    except Exception as e:
        logging.info("No more 'Mehr Anzeigen' button found. Ending load-more loop.")
        return False

def scrape_listings(driver):
    """
    Scrapes all company listings from the current view of the Gelbe Seiten page.
    It finds entries that include a website link and returns a list of records.
    """
    all_records = []

    # Load all available listings by clicking "Mehr Anzeigen" until it disappears
    logging.info("Beginning to load additional results with 'Mehr Anzeigen' clicks...")
    while True:
        tqdm.write("Attempting to load more results...")
        if not click_load_more(driver):
            break

    # Parse the fully loaded page
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # Each listing is wrapped in its own article.mod-Treffer container
    cards = soup.select("article.mod-Treffer")
    logging.info(f"Found {len(cards)} listing containers on the page.")

    # Process each card in a progress bar
    for card in tqdm(cards, desc='Processing listings'):
        # Company name
        name_el = card.select_one("h2.mod-Treffer__name")
        if not name_el:
            continue
        company_name = name_el.get_text(strip=True)

        # Website link (base64‑encoded) within the same card
        link_el = card.select_one(
            "div.contains-icon-big-homepage.webseiteLink "
            "span[data-webseitelink]"
        )
        website = ""
        if link_el:
            encoded_link = link_el["data-webseitelink"]
            try:
                website = base64.b64decode(encoded_link).decode("utf-8")
            except Exception as e:
                logging.error(f"Error decoding website URL for '{company_name}': {e}")

        if website:
            all_records.append({
                "companyName": company_name,
                "website": website
            })
            logging.info(f"Added record for: {company_name}")
        else:
            logging.info(f"Skipped '{company_name}' as no website was found.")

    return all_records

def main():
    # Set up Chrome options for headless browsing.
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    logging.info("Initializing WebDriver.")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        load_page(driver, BASE_URL)
        records = scrape_listings(driver)
    finally:
        driver.quit()
        logging.info("WebDriver closed.")

    # Write the output to the results file.
    try:
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
        logging.info(f"Successfully saved {len(records)} records to {RESULTS_FILE}")
    except Exception as e:
        logging.error(f"Error saving results to file: {e}")

if __name__ == "__main__":
    main()