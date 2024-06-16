import os
from time import sleep
import requests
import json
import re
from bs4 import BeautifulSoup

PROGRESS_FILE_ARTICLES = 'progress_articles.json'
PROGRESS_FILE_NEWS_ARTICLES = 'progress_news_articles.json'
PROGRESS_FILE_QUESTIONS = 'progress_questions.json'
DATA_DIR = 'data'
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def sanitize_filename(filename):
    """
    Sanitizes the given filename by replacing spaces with underscores and removing illegal characters.

    Args:
        filename (str): The original filename.

    Returns:
        str: The sanitized filename.
    """
    filename = filename.strip()
    filename = filename.replace(' ', '_')
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    filename = re.sub(r'[\t\n\r\x0b\x0c]', "", filename)
    return filename


def html_to_text(html_content):
    """
    Converts HTML content to plain text.

    Args:
        html_content (str): The HTML content.

    Returns:
        str: The plain text extracted from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    return text


def remove_templating_patterns(text):
    """
    Removes templating patterns from the text.

    Args:
        text (str): The original text.

    Returns:
        str: The text with templating patterns removed.
    """
    return re.sub(r'\{[^{}]*\}', '', text)


def save_progress(progress_file, page):
    """
    Saves the current page number to the progress file.

    Args:
        progress_file (str): The path to the progress file.
        page (int): The current page number.
    """
    try:
        with open(progress_file, 'w') as f:
            json.dump({"page": page}, f)
    except IOError as e:
        print(f"Error saving progress: {e}")


def load_progress(progress_file):
    """
    Loads the page number from the progress file.

    Args:
        progress_file (str): The path to the progress file.

    Returns:
        int: The page number loaded from the progress file, or 0 if the file does not exist or is invalid.
    """
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                return json.load(f).get("page", 0)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading progress: {e}")
    return 0


def request_with_retries(url, headers, data):
    """
    Makes a POST request with retries in case of failure.

    Args:
        url (str): The URL for the POST request.
        headers (dict): The headers for the request.
        data (str): The JSON data for the request.

    Returns:
        requests.Response: The response object if the request is successful, None otherwise.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}. Attempt {attempt + 1} of {MAX_RETRIES}")
            if attempt < MAX_RETRIES - 1:
                sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Exiting.")
                return None


def process_articles_or_questions(index_name, progress_file, data_dir, combined_json_file):
    """
    Processes articles or questions by making requests to the API and saving the results.

    Args:
        index_name (str): The index name for the API request.
        progress_file (str): The progress file for tracking the current page.
        data_dir (str): The directory where the JSON files will be saved.
        combined_json_file (str): The path to the combined JSON file.
    """
    if os.path.exists(combined_json_file):
        print(f"{combined_json_file} already exists. Skipping scraping for {index_name}.")
        return

    url = "https://search.altibbi.com/api/all"
    headers = {
        "Host": "search.altibbi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Origin": "null",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-GPC": "1",
        "Priority": "u=1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers"
    }

    page = load_progress(progress_file)
    hits_per_page = 100
    has_more = True

    data_dir = os.path.join(DATA_DIR, data_dir)
    os.makedirs(data_dir, exist_ok=True)

    while has_more:
        data = json.dumps([{
            "indexName": index_name,
            "params": {
                "facets": [],
                "highlightPostTag": "__/ais-highlight__",
                "highlightPreTag": "__ais-highlight__",
                "hitsPerPage": hits_per_page,
                "page": page,
                "query": "",
                "tagFilters": ""
            }
        }])

        response = request_with_retries(url, headers, data)
        if response is None:
            break

        try:
            decoded_content = response.content.decode('utf-8')
            decoded_json = json.loads(decoded_content)

            items = decoded_json["results"][0]["hits"]

            if not items:
                has_more = False
                break

            for item in items:
                raw_body = item.get("body", "")
                clean_body = html_to_text(raw_body)
                clean_body = remove_templating_patterns(clean_body)

                item_data = {
                    "objectID": item["objectID"],
                    "title": item.get("title", ""),
                    "body": clean_body,
                    "url": item.get("url", "")
                }

                filename = sanitize_filename(item_data["objectID"]) + ".json"
                try:
                    with open(os.path.join(data_dir, filename), 'w', encoding='utf-8') as f:
                        json.dump(item_data, f, ensure_ascii=False, indent=4)
                except IOError as e:
                    print(f"Error saving item {item_data['objectID']}: {e}")

            save_progress(progress_file, page)
            print(f"Page {page} processed.")

            page += 1
            sleep(3)

        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            print("Decoded content:", decoded_content[:500])
            break

    if not has_more:
        if os.path.exists(progress_file):
            os.remove(progress_file)
        print(f"Scraping {index_name} completed successfully. Progress file removed.")


def combine_json_files(input_directory, output_file):
    """
    Combines all JSON files in the input directory into a single JSON file.

    Args:
        input_directory (str): The directory containing the input JSON files.
        output_file (str): The path to the output JSON file.
    """
    json_list = []

    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_content = json.load(file)
                    json_list.append(json_content)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error reading {file_path}: {e}")

    try:
        with open(output_file, 'w', encoding='utf-8') as output:
            json.dump(json_list, output, ensure_ascii=False, indent=4)
        print(f"Combined JSON file saved to {output_file}")
    except IOError as e:
        print(f"Error saving combined JSON file: {e}")


if __name__ == "__main__":
    print("Starting article scraping...")
    process_articles_or_questions("article-lists", PROGRESS_FILE_ARTICLES, 'articles',
                                  os.path.join(DATA_DIR, 'all_articles.json'))
    print("Combining articles into one JSON file...")
    combine_json_files(os.path.join(DATA_DIR, 'articles'), os.path.join(DATA_DIR, 'all_articles.json'))

    process_articles_or_questions("news_articles", PROGRESS_FILE_NEWS_ARTICLES, 'news_articles',
                                  os.path.join(DATA_DIR, 'all_news_articles.json'))
    print("Combining news articles into one JSON file...")
    combine_json_files(os.path.join(DATA_DIR, 'news_articles'), os.path.join(DATA_DIR, 'all_news_articles.json'))
    print("Starting questions scraping...")

    process_articles_or_questions("questions", PROGRESS_FILE_QUESTIONS, 'questions',
                                  os.path.join(DATA_DIR, 'all_questions.json'))
    print("Combining questions into one JSON file...")
    combine_json_files(os.path.join(DATA_DIR, 'questions'), os.path.join(DATA_DIR, 'all_questions.json'))

    print("Scraping and combining completed.")
