from .base_storage import BaseStorage
from datetime import datetime, timezone

class DynamicStorage(BaseStorage):
    def __init__(self):
        super().__init__("data/dynamic_data.db")
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS dynamic_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price TEXT NOT NULL,
                scraped_at TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def insert_jobs(self, jobs):
        now = datetime.now(timezone.utc).isoformat()
        query = "INSERT INTO dynamic_jobs (title, price, scraped_at) VALUES (?, ?, ?)"
        rows = [(j["title"], j["price"], now) for j in jobs]
        self.conn.executemany(query, rows)
        self.conn.commit()