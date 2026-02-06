from .base_storage import BaseStorage
from .snapshot_storage import SnapshotMixin
from datetime import datetime, timezone

class StaticStorage(BaseStorage, SnapshotMixin):
    def __init__(self):
        super().__init__("data/static_data.db")
        self._create_tables()
        self._create_snapshot_table()  # Add snapshot support

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS job_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                scraped_at TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def insert_jobs(self, jobs):
        now = datetime.now(timezone.utc).isoformat()
        query = "INSERT INTO job_snapshots (title, company, scraped_at) VALUES (?, ?, ?)"
        rows = [(j["title"], j["company"], now) for j in jobs]
        self.conn.executemany(query, rows)
        self.conn.commit()

    def get_all_jobs(self):
        """Retrieve all jobs for change detection comparison."""
        cursor = self.conn.execute("SELECT title, company FROM job_snapshots")
        return [{"title": row[0], "company": row[1]} for row in cursor.fetchall()]