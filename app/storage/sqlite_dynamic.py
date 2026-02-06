from .base_storage import BaseStorage
from .snapshot_storage import SnapshotMixin
from datetime import datetime, timezone

class DynamicStorage(BaseStorage, SnapshotMixin):
    def __init__(self):
        super().__init__("data/dynamic_data.db")
        self._create_tables()
        self._create_snapshot_table()  # Add snapshot support

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

    def get_all_jobs(self):
        """Retrieve all jobs for change detection comparison."""
        cursor = self.conn.execute("SELECT title, price FROM dynamic_jobs")
        return [{"title": row[0], "price": row[1]} for row in cursor.fetchall()]