from scraping.Yahoo_Scraper import YahooScraper
from data.Data_Processor import DataProcessor

## Loading the Scraper 
scraper = YahooScraper(driver='firefox')
# Scraping Latest Article URLs and Counting
url_list = scraper.scrape_market_urls(num_articles=225, homepage_url='https://finance.yahoo.com/news/')
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
