from bs4 import BeautifulSoup
from app.scrapers.dynamic import DynamicScraper
from app.processors.csv_writer import save_to_csv
import time

class DynamicJobMonitor:
    def __init__(self, url: str):
        self.scraper = DynamicScraper(
            url,
            wait_for=".thumbnail",
            headless=True
        )

    def run(self):
        jobs = []
        seen_titles = set() # To prevent duplicates during AJAX transitions
        page = self.scraper.open()

        try:
            page_count = 1
            while True:
                print(f"Scraping page {page_count}...")
                
                # 1. Wait for content to be visible
                page.wait_for_selector(".thumbnail", state="visible")
                
                # 2. Extract content
                soup = BeautifulSoup(page.content(), "lxml")
                items = soup.select(".thumbnail")

                if not items:
                    print("No items found on this page.")
                    break
                
                for job in items:
                    title = job.select_one(".title").get_text(strip=True)
                    price = job.select_one(".price").get_text(strip=True)
                    
                    # Only add if we haven't seen this specific title/price combo yet
                    identifier = f"{title}-{price}"
                    if identifier not in seen_titles:
                        jobs.append({
                            "title": title,
                            "price": price,
                        })
                        seen_titles.add(identifier)

                # 3. Pagination Logic
                next_button = page.query_selector("button.next")

                if not next_button:
                    next_button = page.query_selector("a.next")
                
                if next_button and next_button.is_visible():
                    
                    print("Next button found. Clicking...")
                    
                    # Get the current first item's title to detect when the page changes
                    first_item_before = items[0].select_one(".title").text
                    
                    next_button.click()
                    
                    # Wait for the first item to change (Standard AJAX trick)
                    # This ensures we don't scrape the same page twice
                    try:
                        page.wait_for_function(
                            f"document.querySelector('.title').innerText !== '{first_item_before}'",
                            timeout=5000
                        )
                    except:
                        print("Timeout waiting for content to change, continuing anyway...")
                    
                    page_count += 1
                    page.wait_for_timeout(1000) # Small breath for the UI
                else:
                    print("No clickable 'Next' button found. Ending.")
                    break 

        except Exception as e:
            print(f"An error occurred during scraping: {e}")

        finally:
            self.scraper.close()

        if jobs:
            save_to_csv("dynamic_jobs.csv", jobs)
            print(f"Success! Saved {len(jobs)} items to dynamic_jobs.csv")
        
        return jobs