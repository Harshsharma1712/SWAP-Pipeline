from app.core.logger import setup_logger
from app.monitors.job_monitor import JobMonitor
from app.monitors.dynamic_job_monitor import DynamicJobMonitor
from app.storage.sqlite_static import SQLiteStorage

def main():
    logger = setup_logger()
    storage = SQLiteStorage

    logger.info("Starting scraping engine")

    monitor = JobMonitor("https://realpython.github.io/fake-jobs/")

    monitor_dynamic = DynamicJobMonitor("https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops")

    # jobs = monitor.run()

    jobs = monitor.run()

    logger.info(f"Scraped {len(jobs)} jobs")
    
if __name__ == "__main__":
    main()