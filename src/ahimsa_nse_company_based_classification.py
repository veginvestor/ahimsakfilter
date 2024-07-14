import os
import csv
import logging
import sys

# Configure logging without timestamps
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def read_company_classification_file(filename):
    """Reads a CSV file containing company classifications."""
    with open(filename, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

def determine_category(file_name):
    """Determines the category (GREEN, RED, ORANGE, GREY) based on file name."""
    if "green" in file_name.lower():
        return "GREEN"
    elif "red" in file_name.lower():
        return "RED"
    elif "orange" in file_name.lower():
        return "ORANGE"
    elif "grey" in file_name.lower():
        return "GREY"
    else:
        return "UNKNOWN"

def normalize_company_name(company_name):
    """Normalize company name by stripping and removing trailing dots."""
    return company_name.strip().rstrip('.')

def find_sector_category(sector_name):
    """Finds the category (RED, GREEN, GREY, ORANGE) for a given sector."""
    # Step 1: Read NSE Company Classification file
    nse_file = 'NSE_Company_Classification.csv'
    if not os.path.isfile(nse_file):
        logger.error(f"File '{nse_file}' not found in the current directory.")
        return

    nse_data = read_company_classification_file(nse_file)

    # Normalize sector_name for case insensitivity and trimming whitespace
    normalized_sector_name = sector_name.strip().lower()

    # Log companies found in NSE Company Classification file
    found_companies = []
    for company in nse_data:
        if company['Basic Industry'].strip().lower() == normalized_sector_name:
            found_companies.append(company['Company Name'])
    logger.info(f"Companies found in '{nse_file}' for sector '{sector_name}': {found_companies}")

    # Step 2: Find companies for the given sector
    matched_companies = []
    for company in nse_data:
        if company['Basic Industry'].strip().lower() == normalized_sector_name:
            matched_company_name = normalize_company_name(company['Company Name']).lower()
            matched_companies.append(matched_company_name)  # Normalize company name
            logger.debug(f"Added '{matched_company_name}' to matched_companies list")

    # Step 3: Prepare to store results
    found_results = {}
    not_found_results = []

    # Step 4: Read other CSV files and determine category based on matches
    for matched_company_name in matched_companies:
        found_results[matched_company_name] = {"category": None, "nature_of_activity": None}  # Initialize result

    for file_name in os.listdir('.'):
        if file_name.endswith('.csv') and '_Companies_' in file_name:
            logger.info(f"Searching in '{file_name}' for all matched companies...")
            companies_data = read_company_classification_file(file_name)
            for company_data in companies_data:
                normalized_company_data_name = normalize_company_name(company_data['Company Name']).lower()
                if normalized_company_data_name in matched_companies:  # Compare in a case-insensitive manner
                    if found_results[normalized_company_data_name]["category"] is None:  # Only update if category is not already set
                        category = determine_category(file_name)
                        nature_of_activity = company_data['Nature of Activity']
                        found_results[normalized_company_data_name] = {"category": category, "nature_of_activity": nature_of_activity}
                        logger.info(f"Match found in '{file_name}': Company '{company_data['Company Name']}' matched with category '{category}' and nature of activity '{nature_of_activity}'")

    # Step 5: Separate results into found and not found categories
    for matched_company_name, result in found_results.items():
        if result["category"]:
            logger.info(f"Company '{matched_company_name}' categorized as '{result['category']}' with nature of activity '{result['nature_of_activity']}'")
        else:
            not_found_results.append(matched_company_name)

    # Step 6: Print results for companies with matches found
    logger.info("\n\nCompanies with matches found:")
    for matched_company_name, result in found_results.items():
        if result["category"]:
            logger.info(f"Company '{matched_company_name}' categorized as '{result['category']}' with nature of activity '{result['nature_of_activity']}'")

    # Step 7: Print results for companies with no match found
    if not_found_results:
        logger.info("\n\nCompanies with no match found:")
        for company_name in not_found_results:
            logger.info(f"Company '{company_name}'")

if __name__ == "__main__":
    # Check if sector name is provided as argument
    if len(sys.argv) < 2:
        print("Usage: python program_name.py <sector_name>")
        sys.exit(1)

    sector_name = ' '.join(sys.argv[1:])  # Combine all arguments after the script name
    find_sector_category(sector_name)
