from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import time

class YahooScraper:
    def __init__(self, driver='chrome'):
        """Initializes the YahooScraper"""
        self.driver_choice = driver
        self.title_class = 'cover-title'
        self.body_class = "body"
        self.datetime_class = 'byline-attr-meta-time'
        self.source = "Yahoo Finance"

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
        self.driver = self.setup_driver()
        """Scrapes the Yahoo Finance Page"""
        self.driver.get(target_url) # Open the target URL
        time.sleep(3) # Wait for JavaScript to render
        ## Extracting the Page Source and Parsing with BeautifulSoup
        html = self.driver.page_source # Extracting the HTML (Static Snapshot)
        soup = BeautifulSoup(html, 'html.parser') # Parsing with BeautifulSoup
        ## Verifying Single Symbol Article
        print(target_url)
        ticker_carousel = soup.find('div', class_='carousel-top') # Find the main ticker carousel container
        if not ticker_carousel:
            print(f"❌ Skipping {target_url} — No ticker carousel found.")
            self.driver.quit()
            return None
        symbol_tags = ticker_carousel.find_all('span', class_='symbol yf-1ko1b4u')
        if len(symbol_tags) != 1:
            tickers = [tag.text.strip() for tag in symbol_tags]
            print(f"⚠️ Skipping {target_url} — Multiple tickers found: {tickers}")
            self.driver.quit()
            return None
        ## Getting the Body and Metadata
        title = soup.find('div', class_=self.title_class).text
        symbol = soup.find('span', class_='symbol')
        paragraphs = soup.select(f'div[class*="{self.body_class}"] p')
        body = '\n'.join(p.text for p in paragraphs)
        datetime = soup.find('time', class_=self.datetime_class)['datetime']
        current_url = self.driver.current_url
        ## Closing the Driver
        self.driver.quit()
        ## Returning the Results
        return {
            'title': title,
            'symbol': symbol.text,
            'body': body,
            'datetime': datetime,
            'url': current_url,
            'source': self.source
        }
    
    def scrape_market_urls(self, num_articles=150, homepage_url='https://finance.yahoo.com/news/'):
        """
        Scrapes the latest article URLs from the Yahoo Finance News Homepage.
        """
        self.driver = self.setup_driver()
        self.driver.get(homepage_url)
        time.sleep(3)  # Allow time for the page to load

        collected_urls = set()  # Use a set to avoid duplicates
        scroll_pause = 2 # Pause time between scrolls
        last_height = self.driver.execute_script("return document.body.scrollHeight") # Get Initial Scroll Height

        # Keep scrolling until we have enough unique article links
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
            time.sleep(scroll_pause)  # Wait for new articles to load

            # Check if new content was loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("⚠️ No more content to scroll. Stopping.")
                break  # Stop if no new content is loaded
            last_height = new_height

        return list(collected_urls)
        
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

