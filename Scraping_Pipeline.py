from scraping.Yahoo_Scraper import YahooScraper
from data.data_processor import DataProcessor

## Loading the Scraper 
scraper = YahooScraper(driver='chrome')
# Scraping Latest Article URLs and Counting
url_list = scraper.scrape_market_urls(num_articles=30, homepage_url='https://finance.yahoo.com/news/')
url_list = scraper.clean_urls_from_archive(url_list)
url_counter = 0
valid_urls = 0
scraper_data = []
for url in url_list:
    data = scraper.scrape_data(url)
    if data:  # Only append if it's not None
        scraper_data.append(data)
        valid_urls += 1
    url_counter += 1
print(f"Total URLs Collected: {url_counter}")
print(f"Valid URLs: {valid_urls}")
print("Scraping Complete")
print("====================================")

## Loading the Data Processor
processor = DataProcessor(scraped_dict=scraper_data, archive_path="archive.csv", model_path="model.csv", master_path="master.csv")
processor.check_for_old_duplicates()
processor.append_to_archive_data()
processor.process_and_append_model_data()
print("Data Processing Complete")
print("====================================")
processor.clean_csv_by_date(csv_path="archive.csv",date_column="todaysDate", days=7)
processor.clean_csv_by_date(csv_path="model.csv", date_column="todaysDate" ,days=3)