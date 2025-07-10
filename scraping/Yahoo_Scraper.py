from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
from datetime import datetime
#ash was here

class YahooScraper:
    def __init__(self, driver='chrome'):
        """Initializes the YahooScraper"""
        self.archive_CSV = "archive.csv" 
        self.driver_choice = driver
        self.title_class = 'cover-title yf-1rjrr1'
        self.ticker_caurousel_class = 'carousel-top'
        self.body_class = "body"
        self.dateTime_class = 'byline-attr-meta-time'
        self.source = "Yahoo Finance"
        self.symbol_class = 'symbol yf-90gdtp'

    def setup_driver(self):
        """Sets up the WebDriver"""
        if self.driver_choice == 'chrome':
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument("--log-level=3")  # Only show fatal errors
            options.add_argument("--disable-logging")
            return webdriver.Chrome(options=options)
        elif self.driver_choice == 'firefox':
            options = FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument("--log-level=3")  # Only show fatal errors
            options.add_argument("--disable-logging")
            return webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported driver: {self.driver_choice}")
        
    def scrape_data(self, target_url):
        """Scrapes a Page for Financial Data"""
        ## Setup the WebDriver
        self.driver = self.setup_driver()
        self.driver.get(target_url) # Open the target URL
        time.sleep(2) # Wait for JavaScript to render

        ## Extracting the Page Source and Parsing with BeautifulSoup
        html = self.driver.page_source # Extracting the HTML (Static Snapshot)
        soup = BeautifulSoup(html, 'html.parser') # Parsing with BeautifulSoup

        ## Verifying Single Symbol Article
        print(f"Parsing: {target_url}")
        ticker_carousel = soup.find('div', class_=self.ticker_caurousel_class) # Find the main ticker carousel container
        if not ticker_carousel:
            print(f"ERROR: Skipping {target_url} — No ticker carousel found.")
            self.driver.quit()
            return None
        symbol_tags = ticker_carousel.find_all('span', class_=self.symbol_class) # Find all symbols in the ticker carousel
        if len(symbol_tags) != 1:
            tickers = [tag.text.strip() for tag in symbol_tags]
            print(f"ERROR: Skipping {target_url} — Multiple tickers found: {tickers}")
            self.driver.quit()
            return None
        ## Getting the Body and Metadata
        title = soup.find('h1', class_=self.title_class).text
        symbol = soup.find('span', class_=self.symbol_class) # Find the symbol in the ticker carousel
        paragraphs = soup.select(f'div[class*="{self.body_class}"] p')
        body = '\n'.join(p.text for p in paragraphs)
        dateTime = soup.find('time', class_=self.dateTime_class)['datetime']
        current_url = self.driver.current_url
        ## Closing the Driver
        self.driver.quit()
        ## Returning the Results
        return {
            'title': title,
            'symbol': symbol.text,
            'body': body,
            'datetime': dateTime,
            'url': current_url,
            'source': self.source,
            'todaysDate': datetime.now()
        }
    
    def scrape_market_urls(self, num_articles=150, homepage_url='https://finance.yahoo.com/news/'):
        """
        Scrapes the latest article URLs from the Yahoo Finance News Homepage.
        """
        ## Setup the WebDriver
        self.driver = self.setup_driver()
        self.driver.get(homepage_url)
        time.sleep(2)  # Allow time for the page to load

        ## Setting Scrolling and Data Collection
        collected_urls = set()  # Use a set to avoid duplicates
        last_height = self.driver.execute_script("return document.body.scrollHeight") # Get Initial Scroll Height

        ## Begin Scrolling and Collecting URLs
        print(f"Collecting URLs from {homepage_url}...")
        while len(collected_urls) < num_articles:
            # Get the full HTML after scroll
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            # Find all anchor tags that link to articles
            for a_tag in soup.find_all('a', class_='subtle-link'): # Subtle Link Class Holds Link Information
                href = a_tag.get('href') # HREF is Hyperlink Reference
                if href and "/news/" in href and href.endswith(".html"):# Filter for news articles
                    # Construct the full URL
                    full_url = href if href.startswith("http") else f"https://finance.yahoo.com{href}"
                    collected_urls.add(full_url) # Sets Automatically Handle Duplicates
            # Scroll to the bottom of the page to load more content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new articles to load
            # Check if new content was loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("FINISHED: NO NEW CONTENT LOADED")
                break  # Stop if no new content is loaded
            last_height = new_height

        return list(collected_urls)
        
    def clean_urls_from_archive(self, urlList):
        """
        Removes URLs from self.url_list that are already present in the archive CSV.
        """
        if os.path.exists(self.archive_CSV):
            # Load archive
            archive_df = pd.read_csv(self.archive_CSV)
            # Get set of archived URLs for fast lookup
            archived_urls = set(archive_df['url'])
            # Filter out duplicates
            urlList = [url for url in urlList if url not in archived_urls]
            return urlList
        else:
            return urlList

if __name__ == "__main__":
    scraper = YahooScraper(driver='chrome')
    target_url = "https://finance.yahoo.com/news/nuvation-bio-inc-nuvb-top-214015334.html" # Multiple Sentiment Extraction Error
    scraper_data = scraper.scrape_data(target_url)
    print("====================================")

    target_url = "https://finance.yahoo.com/news/nvidia-nvda-spend-billions-us-182941880.html" # Typical Data Collection
    scraper_data = scraper.scrape_data(target_url)
    print(scraper_data['title'])
    print(scraper_data['symbol'])
    print(scraper_data['body'])
    print(scraper_data['datetime'])
    print(scraper_data['url'])
    print(scraper_data['source'])
    print("====================================")

    urls = scraper.scrape_market_urls(num_articles=250) # Scalable URL Collection
    i=0
    for url in urls:
        print(url)
        i+=1
    print(f"Total URLs Collected: {i}")
    print("====================================")

