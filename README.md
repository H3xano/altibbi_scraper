# Altibbi Scraper

This project is a web scraper designed to collect articles and questions from the Altibbi website. The scraper can handle interruptions by saving its progress and can be resumed later. It includes error handling and retry mechanisms to ensure robust data collection. At the end of the scraping process, all collected data is combined into separate large JSON files for articles, news articles, and questions.

## Features

- Scrapes articles, news articles, and questions from the Altibbi website.
- Saves progress to allow pause and resume functionality.
- Implements retry mechanisms for failed requests.
- Combines individual JSON files into separate large JSON files at the end of the process.
- Skips scraping if the combined JSON file already exists.

## Requirements

- Python 3.6 or higher
- `requests` library
- `beautifulsoup4` library

## Installation

1. Clone the repository:

2. Change to the project directory:
   ```bash
   cd altibbi-scraper
   ```
3. Install the required libraries:
   ```bash
   pip install requests beautifulsoup4
   ```

## Usage

1. Run the scraper to collect articles, news articles, and questions:
   ```bash
   python scraper.py
   ```
   The script will scrape data, saving progress in `progress_articles.json`, `progress_news_articles.json`, and `progress_questions.json` respectively.

2. To resume scraping after an interruption, simply run the script again:
   ```bash
   python scraper.py
   ```

3. The collected data will be saved as individual JSON files in the `data/articles`, `data/news_articles`, and `data/questions` directories.

4. After scraping, the script will combine all individual JSON files into `all_articles.json`, `all_news_articles.json`, and `all_questions.json` in the `data` directory.

## File Structure

```
altibbi-scraper/
├── data/
│   ├── articles/
│   ├── news_articles/
│   ├── questions/
│   ├── all_articles.json
│   ├── all_news_articles.json
│   └── all_questions.json
├── progress_articles.json
├── progress_news_articles.json
├── progress_questions.json
├── scraper.py
└── README.md
```

## Functions

### `sanitize_filename(filename)`
Sanitizes the given filename by replacing spaces with underscores and removing illegal characters.

### `html_to_text(html_content)`
Converts HTML content to plain text.

### `remove_templating_patterns(text)`
Removes templating patterns from the text.

### `save_progress(progress_file, page)`
Saves the current page number to the progress file.

### `load_progress(progress_file)`
Loads the page number from the progress file.

### `request_with_retries(url, headers, data)`
Makes a POST request with retries in case of failure.

### `process_articles_or_questions(index_name, progress_file, data_dir, combined_json_file)`
Processes articles or questions by making requests to the API and saving the results.

### `combine_json_files(input_directory, output_file)`
Combines all JSON files in the input directory into a single JSON file.

## Example

To scrape articles, news articles, and questions from Altibbi, run the following command:

```bash
python scraper.py
```

This will scrape data and save individual JSON files in the `data/articles`, `data/news_articles`, and `data/questions` directories. After the scraping is complete, the script will combine these files into `all_articles.json`, `all_news_articles.json`, and `all_questions.json`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue.

## Contact

If you have any questions or suggestions, feel free to reach out to me. 