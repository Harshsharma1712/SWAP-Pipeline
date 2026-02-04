from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, url: str):
        self.url = url
    
    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def parse(self, content):
        pass

    def run(self):
        content = self.fetch()
        return self.parse(content)
