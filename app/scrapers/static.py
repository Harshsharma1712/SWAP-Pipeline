import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper

class StaticScraper(BaseScraper):
    def fetch(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        return response.text
    
    def parse(self, content):
        return BeautifulSoup(content, "lxml")
