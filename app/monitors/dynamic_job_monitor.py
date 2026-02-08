from bs4 import BeautifulSoup
from app.scrapers.dynamic import DynamicScraper
from app.processors.csv_writer import save_to_csv
from app.processors.cleaner import (
    DataCleaner,
    remove_duplicates,
    validate_required_fields,
    normalize_text_fields,
)
from app.storage.sqlite_dynamic import DynamicStorage
from app.detection.change_detector import ChangeDetector
from app.detection.base_detector import ChangeReport
from app.notifiers.notification_manager import NotificationManager

class DynamicJobMonitor:
    def __init__(self, url: str, enable_change_detection: bool = True):
        self.scraper = DynamicScraper(
            url,
            wait_for=".thumbnail",
            headless=True
        )

        self.storage = DynamicStorage()
        self.source_name = "dynamic_jobs"
        
        # Change detection setup
        self.enable_change_detection = enable_change_detection
        self.detector = ChangeDetector(
            key_fields=["title"],  # Unique identifier
            compare_fields=["title", "price"]  # Fields to track for changes
        )
        # Use NotificationManager for multi-channel notifications
        self.notification_manager = NotificationManager(include_console=True)

        self.cleaner = DataCleaner(steps=[
            lambda d: remove_duplicates(d, ["title", "price"]),
            lambda d: validate_required_fields(d, ["title", "price"]),
            lambda d: normalize_text_fields(d, ["title", "price"]),
        ])


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
            # Change Detection
            if self.enable_change_detection:
                # Use storage's built-in snapshot methods (stored in dynamic_data.db)
                old_data = self.storage.get_latest_snapshot(self.source_name)
                
                if old_data is not None:
                    # Compare with previous data
                    changes = self.detector.detect(old_data, jobs)
                    
                    # Send notifications to all channels (console, email, telegram)
                    self.notification_manager.notify_all(changes, self.source_name)
                    
                    if not changes.has_changes:
                        print("✅ No changes detected. Skipping data save.")
                        return jobs
                    
                    # Update snapshot with new data
                    self.storage.save_snapshot(self.source_name, jobs)
                    self.storage.cleanup_old_snapshots(self.source_name, keep_count=10)
                else:
                    # First run - create initial snapshot
                    print("\n" + "=" * 60)
                    print("📦 FIRST RUN - Initial Data Capture")
                    print("=" * 60)
                    print(f"📊 Captured {len(jobs)} items as baseline.")
                    print("   Next run will compare against this snapshot.")
                    print("=" * 60 + "\n")
                    
                    # Save initial snapshot
                    self.storage.save_snapshot(self.source_name, jobs)

            save_to_csv("dynamic_jobs.csv", jobs)
            self.storage.insert_jobs(jobs)
            print(f"Success! Saved {len(jobs)} items to dynamic_jobs.csv")
        
        return jobs