from app.core.logger import setup_logger
from app.monitors.job_monitor import JobMonitor
from app.monitors.dynamic_job_monitor import DynamicJobMonitor

def main():
    logger = setup_logger()

    logger.info("Starting scraping engine")

    static_monitor = JobMonitor("https://realpython.github.io/fake-jobs/")

    dynamic_monitor = DynamicJobMonitor("https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops")

    phones = DynamicJobMonitor("https://webscraper.io/test-sites/e-commerce/ajax/phones/touch")

    # phones_data = phones.run()

    # jobs = dynamic_monitor.run()

    jobs = phones.run()

    logger.info(f"Scraped {len(jobs)} jobs")
    # logger.info(f"Scraped {len(jobs)} jobs")
    
if __name__ == "__main__":
    main()