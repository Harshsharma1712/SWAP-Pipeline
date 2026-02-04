from app.core.logger import setup_logger
from app.monitors.job_monitor import JobMonitor

def main():
    logger = setup_logger()
    logger.info("Starting static scraping test")

    monitor = JobMonitor("https://realpython.github.io/fake-jobs/")
    jobs = monitor.run()

    logger.info(f"Scraped {len(jobs)} jobs")

if __name__ == "__main__":
    main()