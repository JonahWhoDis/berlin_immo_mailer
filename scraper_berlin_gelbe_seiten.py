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
RESULTS_FILE = "gelbeseiten_results_verwaltung.json"
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

    # Use a tqdm progress bar for the load more loop (limited to 5 iterations for testing).
    logging.info("Beginning to load additional results with 'Mehr Anzeigen' clicks...")
    while True:
        tqdm.write("Attempting to load more results...")
        if not click_load_more(driver):
            break

    # Parse the fully loaded page source using BeautifulSoup.
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # Find all listings by locating the header elements with the company names.
    listings = soup.find_all("h2", class_="mod-Treffer__name")
    logging.info(f"Found {len(listings)} listings on the page.")

    # Process each listing with a live progress bar.
    for listing in tqdm(listings, desc='Processing listings'):
        company_name = listing.get_text(strip=True)

        # Locate the website container near the company name.
        website_div = listing.find_next("div", class_="contains-icon-big-homepage webseiteLink")
        website = ""
        if website_div:
            span = website_div.find("span", attrs={"data-webseitelink": True})
            if span:
                encoded_link = span["data-webseitelink"]
                try:
                    website = base64.b64decode(encoded_link).decode("utf-8")
                except Exception as e:
                    logging.error(f"Error decoding website URL for '{company_name}': {e}")
        if website:
            record = {"companyName": company_name, "website": website}
            all_records.append(record)
            logging.info(f"Added record for: {company_name}")
        else:
            logging.info(f"Skipped '{company_name}' as no website was found.")

    return all_records

def main():
    # Set up Chrome options for headless browsing.
    chrome_options = Options()
    chrome_options.add_argument("--headless")
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