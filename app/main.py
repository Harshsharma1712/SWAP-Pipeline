"""
SWMAP Pipeline - Main Entry Point
Interactive CLI to run different scrapers and features
"""
from app.core.logger import setup_logger
from app.monitors.job_monitor import JobMonitor
from app.monitors.dynamic_job_monitor import DynamicJobMonitor


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("  🚀 SWMAP - Web Scraping & Monitoring Pipeline")
    print("  📊 Change Detection Engine v0.5")
    print("=" * 60)


def print_menu():
    """Print the main menu options."""
    print("\n📋 Available Features:")
    print("-" * 40)
    print("  [1] 🌐 Static Scraper")
    print("      → Scrape: realpython.github.io/fake-jobs")
    print()
    print("  [2] ⚡ Dynamic Scraper (AJAX/JS)")
    print("      → Scrape: webscraper.io/test-sites/e-commerce")
    print()
    print("  [3] 🔄 Run Both Scrapers")
    print()
    print("  [0] ❌ Exit")
    print("-" * 40)


def run_static_scraper(logger):
    """Run the static job scraper."""
    print("\n🌐 Starting Static Scraper...")
    print("   Target: https://realpython.github.io/fake-jobs/")
    print("-" * 40)
    
    monitor = JobMonitor("https://realpython.github.io/fake-jobs/")
    jobs = monitor.run()
    
    logger.info(f"Static scraper completed: {len(jobs)} jobs scraped")
    print(f"\n✅ Static Scraper Complete! Found {len(jobs)} jobs.")
    return jobs


def run_dynamic_scraper(logger):
    """Run the dynamic job scraper."""
    print("\n⚡ Starting Dynamic Scraper...")
    print("   Target: https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops")
    print("-" * 40)
    
    monitor = DynamicJobMonitor(
        "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops"
    )
    jobs = monitor.run()
    
    logger.info(f"Dynamic scraper completed: {len(jobs)} items scraped")
    print(f"\n✅ Dynamic Scraper Complete! Found {len(jobs)} items.")
    return jobs


def main():
    """Main entry point with interactive menu."""
    logger = setup_logger()
    logger.info("SWMAP Pipeline started")
    
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("\n👉 Enter your choice (0-3): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        
        if choice == "1":
            run_static_scraper(logger)
            
        elif choice == "2":
            run_dynamic_scraper(logger)
            
        elif choice == "3":
            print("\n🔄 Running Both Scrapers...")
            run_static_scraper(logger)
            run_dynamic_scraper(logger)
            print("\n✅ All scrapers complete!")
            
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please enter 0, 1, 2, or 3.")
        
        # Ask if user wants to continue
        try:
            again = input("\n🔁 Run another scraper? (y/n): ").strip().lower()
            if again != 'y':
                print("\n👋 Goodbye!")
                break
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break


if __name__ == "__main__":
    main()
