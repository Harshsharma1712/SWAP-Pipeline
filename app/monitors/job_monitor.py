from app.scrapers.static import StaticScraper
from app.processors.csv_writer import save_to_csv
from app.processors.cleaner import (
    DataCleaner,
    remove_duplicates,
    validate_required_fields,
    normalize_text_fields,
)
from app.storage.sqlite_static import SQLiteStorage

class JobMonitor:
    def __init__(self, url: str):
        self.scraper = StaticScraper(url)
    
        self.cleaner = DataCleaner(steps=[
                lambda d: remove_duplicates(d, ["title", "price"]),
                lambda d: validate_required_fields(d, ["title", "price"]),
                lambda d: normalize_text_fields(d, ["title", "price"]),
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

        save_to_csv("jobs.csv", jobs)

        storage = SQLiteStorage()
        storage.insert_jobs(jobs)

        return jobs