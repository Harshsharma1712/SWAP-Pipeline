from app.scrapers.static import StaticScraper
from app.processors.csv_writer import save_to_csv
from app.processors.cleaner import (
    DataCleaner,
    remove_duplicates,
    validate_required_fields,
    normalize_text_fields,
)
from app.storage.sqlite_static import StaticStorage
from app.detection.change_detector import ChangeDetector
from app.detection.base_detector import ChangeReport
from app.notifiers.notification_manager import NotificationManager

class JobMonitor:
    def __init__(self, url: str, enable_change_detection: bool = True):
        self.scraper = StaticScraper(url)
        self.storage = StaticStorage()
        self.source_name = "static_jobs"
        
        # Change detection setup
        self.enable_change_detection = enable_change_detection
        self.detector = ChangeDetector(
            key_fields=["title"],  # Unique identifier
            compare_fields=["title", "company"]  # Fields to track for changes
        )
        # Use NotificationManager for multi-channel notifications
        self.notification_manager = NotificationManager(include_console=True)
    
        self.cleaner = DataCleaner(steps=[
                lambda d: remove_duplicates(d, ["title", "company"]),
                lambda d: validate_required_fields(d, ["title", "company"]),
                lambda d: normalize_text_fields(d, ["title", "company"]),
            ])

    def run(self):
        soup = self.scraper.run()
        jobs = []

        for job in soup.select(".card-content"):  # example selector
            title = job.select_one(".title")
            company = job.select_one(".company")

            jobs.append({
                "title": title.text.strip() if title else None,
                "company": company.text.strip() if company else None,
            })

        if jobs:
            # Change Detection
            if self.enable_change_detection:
                # Use storage's built-in snapshot methods (stored in static_data.db)
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

            save_to_csv("jobs.csv", jobs)
            self.storage.insert_jobs(jobs)

        return jobs