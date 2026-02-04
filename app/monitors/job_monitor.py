from app.scrapers.static import StaticScraper
from app.processors.csv_writer import save_to_csv

class JobMonitor:
    def __init__(self, url: str):
        self.scraper = StaticScraper(url)

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
        return jobs