from app.core.logger import setup_logger
from app.monitors.job_monitor import JobMonitor
from app.monitors.dynamic_job_monitor import DynamicJobMonitor

def main():
    logger = setup_logger()
    logger.info("Starting static scraping test")

    monitor = JobMonitor("https://realpython.github.io/fake-jobs/")

    monitor_dynamic = DynamicJobMonitor("https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops")

    # jobs = monitor.run()

    jobs = monitor_dynamic.run()

    logger.info(f"Scraped {len(jobs)} jobs")

if __name__ == "__main__":
    main()