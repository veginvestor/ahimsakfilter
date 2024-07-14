import os
import pandas as pd
from fuzzywuzzy import fuzz
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supporting words to ignore in matching
SUPPORTING_WORDS = {'&', 'and', '-', 'or'}

# Configurable threshold for logging matched records even with low score
LOGGING_SCORE_THRESHOLD = 60

def load_data_files():
    industry_files = []
    company_files = []
    for file in os.listdir('.'):
        if file.endswith('.txt') and '_Industry_' in file:
            industry_files.append(file)
        elif file.endswith('.csv') and '_Companies_' in file:
            company_files.append(file)
    return industry_files, company_files

def load_industry_sectors(file_path):
    with open(file_path, 'r') as file:
        sectors = file.read().splitlines()
    return sectors

def split_and_normalize(text):
    words = text.split()
    return [word.strip().lower() for word in words if word.strip().lower() not in SUPPORTING_WORDS]

def categorize_sector(sector, data_files):
    best_match = ("", 0, "", "")
    max_score = 0
    sector_words = split_and_normalize(sector)
    sector_phrase = " ".join(sector_words)
    matched_logs = set()  # To store unique matches
    for file in data_files:
        try:
            with open(file, 'r') as f:
                lines = f.readlines()
                for index, line in enumerate(lines):
                    line_words = split_and_normalize(line)
                    for i in range(len(line_words) - len(sector_words) + 1):
                        sublist = line_words[i:i + len(sector_words)]
                        joined_sublist = " ".join(sublist)
                        score = fuzz.ratio(sector_phrase, joined_sublist)
                        if score > best_match[1]:
                            best_match = (joined_sublist, score, file, index + 1)
                        if score > max_score:
                            max_score = score
                        if score >= LOGGING_SCORE_THRESHOLD:
                            match_key = (joined_sublist, file, index + 1)
                            if match_key not in matched_logs:
                                matched_logs.add(match_key)
                                logging.info(f"Matched '{sector}' with '{joined_sublist}' in file '{file}' at line {index + 1}, Score: {score}")
        except Exception as e:
            logging.error(f"Error reading file {file}: {e}")
    return best_match, max_score

def categorize_with_company_files(sector, company_files):
    best_match = ("", 0, "", "")
    max_score = 0
    sector_words = split_and_normalize(sector)
    sector_phrase = " ".join(sector_words)
    matched_logs = set()  # To store unique matches
    for file in company_files:
        try:
            df = pd.read_csv(file)
            activity_column = 'Nature Of Activity' if 'Nature Of Activity' in df.columns else 'Nature of Activity'
            if activity_column not in df.columns:
                logging.error(f"'{activity_column}' column not found in file {file}")
                continue
            for index, row in df.iterrows():
                activity = row[activity_column]
                if not isinstance(activity, str):
                    continue
                activity_words = split_and_normalize(activity)
                for i in range(len(activity_words) - len(sector_words) + 1):
                    sublist = activity_words[i:i + len(sector_words)]
                    joined_sublist = " ".join(sublist)
                    score = fuzz.ratio(sector_phrase, joined_sublist)
                    if score > best_match[1]:
                        best_match = (joined_sublist, score, file, index + 2)
                    if score > max_score:
                        max_score = score
                    if score >= LOGGING_SCORE_THRESHOLD:
                        match_key = (joined_sublist, file, index + 2)
                        if match_key not in matched_logs:
                            matched_logs.add(match_key)
                            logging.info(f"Matched '{sector}' with '{joined_sublist}' in file '{file}' at line {index + 2}, Score: {score}")
        except Exception as e:
            logging.error(f"Error reading file {file}: {e}")
    return best_match, max_score

def determine_category(file_name):
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

def main():
    industry_sectors = load_industry_sectors('NSE_BasicSector_List.txt')
    industry_files, company_files = load_data_files()

    results = []
    category_counts = {'GREEN': 0, 'RED': 0, 'ORANGE': 0, 'GREY': 0, 'UNKNOWN': 0}
    uncategorized_count = 0

    for sector in industry_sectors:
        logging.debug(f"Categorizing sector: {sector}")
        best_match, max_score = categorize_sector(sector, industry_files)
        category = determine_category(best_match[2])
        if best_match[1] >= 85:
            category_counts[category] += 1
            comments = f"Matched '{sector}' with '{best_match[0]}' in file '{best_match[2]}' at line {best_match[3]}"
        else:
            category = 'UNCATEGORIZED'
            uncategorized_count += 1
            comments = "No match found"
        results.append([sector, category, comments, max_score])

    # Process uncategorized records with company files
    for i, (sector, category, comments, max_score) in enumerate(results):
        if category == 'UNCATEGORIZED':
            logging.info(f"Re-categorizing uncategorized sector: {sector}")
            best_match, max_score = categorize_with_company_files(sector, company_files)
            if best_match[1] >= 85:
                category = determine_category(best_match[2])
                category_counts[category] += 1
                uncategorized_count -= 1
                comments = f"Matched with '{best_match[0]}' in file '{best_match[2]}' at line {best_match[3]}"
            else:
                category = ''
                comments = f"No match found in company files. The last match was '{best_match[0]}' in file '{best_match[2]}' at line {best_match[3]}"
            results[i] = [sector, category, comments, max_score]

    # Create a DataFrame and save to CSV
    df_results = pd.DataFrame(results, columns=['Industry Sector', 'Category', 'Comments', 'Match Score'])
    df_results.to_csv('categorized_industry_sectors.csv', index=False)

    # Print statistics
    logging.info("Categorization complete.")
    logging.info(f"Total sectors categorized: {len(industry_sectors) - uncategorized_count}")
    logging.info(f"Total sectors uncategorized: {uncategorized_count}")
    for category, count in category_counts.items():
        logging.info(f"{category}: {count}")

    # Log max score found
    max_scores = [result[3] for result in results if result[3] > 0]
    if max_scores:
        max_score = max(max_scores)
        logging.info(f"Max score found during categorization: {max_score}")

if __name__ == "__main__":
    main()
