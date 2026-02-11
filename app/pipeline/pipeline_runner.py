"""
Pipeline Runner - Generic execution engine for config-driven pipelines.
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from app.pipeline.config_loader import PipelineConfig
from app.pipeline.scraper_factory import ScraperFactory
from app.storage.sqlite_dynamic import DynamicStorage
from app.storage.sqlite_static import StaticStorage
from app.detection.change_detector import ChangeDetector
from app.notifiers.notification_manager import NotificationManager
from app.processors.csv_writer import save_to_csv


class PipelineRunner:
    """
    Generic pipeline runner that executes scraping based on YAML config.
    Works with both static and dynamic scrapers.
    """

    def __init__(self, config: PipelineConfig):
        """
        Initialize pipeline runner with configuration.
        
        Args:
            config: Pipeline configuration from YAML
        """
        self.config = config
        self.scraper = ScraperFactory.create(config)
        
        # Use appropriate storage based on type
        if config.type == "static":
            self.storage = StaticStorage()
        else:
            self.storage = DynamicStorage()
        
        # Setup change detection
        self.detector = ChangeDetector(
            key_fields=[list(config.field_selectors.keys())[0]],  # First field as key
            compare_fields=list(config.field_selectors.keys())
        )
        
        # Setup notifications
        self.notification_manager = NotificationManager(include_console=True)

    def run(self) -> List[Dict[str, Any]]:
        """
        Execute the pipeline based on config type.
        
        Returns:
            List of scraped items
        """
        print(f"\n{'='*60}")
        print(f"🚀 Running Pipeline: {self.config.name}")
        print(f"   URL: {self.config.url}")
        print(f"   Type: {self.config.type}")
        print(f"{'='*60}")
        
        if self.config.type == "static":
            return self._run_static()
        else:
            return self._run_dynamic()

    def _run_static(self) -> List[Dict[str, Any]]:
        """Execute static pipeline."""
        soup = self.scraper.run()
        items = self._parse_items(soup)
        return self._process_results(items)

    def _run_dynamic(self) -> List[Dict[str, Any]]:
        """Execute dynamic pipeline with pagination support."""
        items = []
        seen_ids = set()
        page = self.scraper.open()

        try:
            page_count = 1
            while True:
                print(f"Scraping page {page_count}...")
                
                # Wait for content
                if self.config.wait_for:
                    page.wait_for_selector(self.config.wait_for, state="visible")
                
                # Parse content
                soup = BeautifulSoup(page.content(), "lxml")
                page_items = self._parse_items(soup)
                
                if not page_items:
                    print("No items found on this page.")
                    break
                
                # Deduplicate
                for item in page_items:
                    item_id = self._get_item_id(item)
                    if item_id not in seen_ids:
                        items.append(item)
                        seen_ids.add(item_id)
                
                # Handle pagination
                if not self.config.pagination_enabled:
                    break
                
                next_button = self._find_next_button(page)
                if next_button and next_button.is_visible():
                    print("Next button found. Clicking...")
                    
                    # Get first item before click for change detection
                    first_item_before = page_items[0] if page_items else None
                    first_key = list(self.config.field_selectors.keys())[0]
                    first_val = first_item_before.get(first_key, "") if first_item_before else ""
                    
                    next_button.click()
                    
                    # Wait for content change
                    try:
                        selector = self.config.field_selectors.get(first_key, ".title")
                        page.wait_for_function(
                            f"document.querySelector('{selector}')?.innerText !== '{first_val}'",
                            timeout=5000
                        )
                    except:
                        print("Timeout waiting for content change...")
                    
                    page_count += 1
                    page.wait_for_timeout(1000)
                else:
                    print("No next button found. Ending pagination.")
                    break

        except Exception as e:
            print(f"❌ Error during scraping: {e}")
        finally:
            self.scraper.close()

        return self._process_results(items)

    def _parse_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse items from soup using config selectors."""
        items = []
        containers = soup.select(self.config.container_selector)
        
        for container in containers:
            item = {}
            for field_name, selector in self.config.field_selectors.items():
                element = container.select_one(selector)
                item[field_name] = element.get_text(strip=True) if element else None
            items.append(item)
        
        return items

    def _get_item_id(self, item: Dict[str, Any]) -> str:
        """Generate unique ID for an item."""
        values = [str(v) for v in item.values() if v]
        return "-".join(values)

    def _find_next_button(self, page):
        """Find the next pagination button."""
        selectors = self.config.next_button_selector.split(",")
        for selector in selectors:
            button = page.query_selector(selector.strip())
            if button:
                return button
        return None

    def _process_results(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process scraped items - change detection, notifications, storage."""
        if not items:
            print("⚠️ No items scraped.")
            return items
        
        source_name = self.config.source_name
        
        # Change detection
        if self.config.change_detection:
            old_data = self.storage.get_latest_snapshot(source_name)
            
            if old_data is not None:
                changes = self.detector.detect(old_data, items)
                
                # Notify all channels
                if self.config.notifications:
                    self.notification_manager.notify_all(changes, source_name)
                
                if not changes.has_changes:
                    print("✅ No changes detected. Skipping save.")
                    return items
                
                # Save new snapshot
                self.storage.save_snapshot(source_name, items)
                self.storage.cleanup_old_snapshots(source_name, keep_count=10)
            else:
                print("\n" + "=" * 60)
                print("📦 FIRST RUN - Initial Data Capture")
                print("=" * 60)
                print(f"📊 Captured {len(items)} items as baseline.")
                print("=" * 60 + "\n")
                self.storage.save_snapshot(source_name, items)
        
        # Save to CSV
        csv_filename = f"{source_name}.csv"
        save_to_csv(csv_filename, items)
        
        # Save to database
        self.storage.insert_jobs(items)
        print(f"✅ Saved {len(items)} items to {csv_filename} and database")
        
        return items
