from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import time

class YahooScraper:
    def __init__(self, target_url, driver='chrome'):
        """Initializes the YahooScraper"""
        self.target_url = target_url
        self.driver_choice = driver
        self.title_class = 'cover-title'
        self.body_class = "body"
        self.datetime_class = 'byline-attr-meta-time'
        self.source = "Yahoo Finance"
        self.driver = self.setup_driver()

    def setup_driver(self):
        """Sets up the WebDriver"""
        if self.driver_choice == 'chrome':
            options = ChromeOptions()
            # options.add_argument('--headless')
            return webdriver.Chrome(options=options)
        elif self.driver_choice == 'firefox':
            options = FirefoxOptions()
            options.add_argument('--headless')
            return webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported driver: {self.driver_choice}")
        
    def scrape(self):
        """Scrapes the Yahoo Finance Page"""
        self.driver.get(self.target_url) # Open the target URL
        time.sleep(3) # Wait for JavaScript to render
        ## Extracting the Page Source and Parsing with BeautifulSoup
        html = self.driver.page_source # Extracting the HTML (Static Snapshot)
        soup = BeautifulSoup(html, 'html.parser') # Parsing with BeautifulSoup
        # Getting the Title and Body
        title = soup.find('div', class_=self.title_class).text
        symbol = soup.find('span', class_='symbol')
        paragraphs = soup.select(f'div[class*="{self.body_class}"] p')
        body = '\n'.join(p.text for p in paragraphs)
        datetime = soup.find('time', class_=self.datetime_class)['datetime']
        source = "Yahoo Finance"
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
    
if __name__ == "__main__":
    target_url = "https://finance.yahoo.com/news/amazon-could-beat-tesla-massive-072500717.html"
    scraper = YahooScraper(target_url, driver='chrome').scrape()
    print(scraper['title'])
    print(scraper['symbol'])
    print(scraper['body'])
    print(scraper['datetime'])
    print(scraper['url'])
    print(scraper['source'])