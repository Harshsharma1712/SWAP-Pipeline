"""
SWMAP Pipeline - Main Entry Point
Interactive CLI to run different scrapers and features
"""
from app.monitors.job_monitor import JobMonitor
from app.monitors.dynamic_job_monitor import DynamicJobMonitor

job_monitor_url = "https://realpython.github.io/fake-jobs/"
dynamic_laptop_url = "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops"
dynamic_phones_url = "https://webscraper.io/test-sites/e-commerce/ajax/phones/touch"


def main():
   
    print("Select Engine:")
    print("1. Static Job Monitor")
    print("2. Dynamic Scraper (Laptops)")
    print("3. Dynamic Scraper (Phones)")

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        monitor = JobMonitor(job_monitor_url)
        monitor.run()
    
    elif choice == "2":
        monitor = DynamicJobMonitor(dynamic_laptop_url)
        monitor.run()
    
    elif choice == "3":
        monitor = DynamicJobMonitor(dynamic_phones_url)
        monitor.run()
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
