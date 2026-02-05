from playwright.sync_api import sync_playwright

class DynamicScraper:
    def __init__(self, url, wait_for=None, headless=True, timeout=30_000):
        self.url = url
        self.wait_for = wait_for
        self.headless = headless
        self.timeout = timeout

    def open(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()

        self.page.goto(self.url, timeout=self.timeout)
        if self.wait_for:
            self.page.wait_for_selector(self.wait_for)

        return self.page

    def close(self):
        self.browser.close()
        self.playwright.stop()
