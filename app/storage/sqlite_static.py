import sqlite3
from datetime import datetime, timezone
from typing import List, Dict

DB_PATH = "data/static_data.db"


class SQLiteStorage:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS job_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            scraped_at TEXT NOT NULL
        );
        """
        self.conn.execute(query)
        self.conn.commit()
    
    def insert_jobs(self, jobs: List[Dict]):
        now = datetime.now(timezone.utc).isoformat()

        query = """
        INSERT INTO job_snapshots (title, company, scraped_at)
        VALUES (?, ?, ?)
        """

        rows = [
            (job["title"], job["company"], now)
            for job in jobs
        ]

        self.conn.executemany(query, rows)
        self.conn.commit()
    
    def fetch_latest_jobs(self):
        query = """
        SELECT title, company, scraped_at
        FROM job_snapshots
        WHERE scraped_at = (
            SELECT MAX(scraped_at) FROM job_snapshots
        )
        """
        return self.conn.execute(query).fetchall()
    
    def fetch_jobs_by_date(self, date: str):
        query = """
        SELECT title, company, scraped_at
        FROM job_snapshots
        WHERE DATE(scraped_at) = DATE(?)
        """
        return self.conn.execute(query, (date,)).fetchall()

    # use with caution
    def clear_all_data(self):
        self.conn.execute("DELETE FROM job_snapshots")
        self.conn.commit()

        self.conn.execute("VACUUM")
    
    def delete_older_than(self, days: int):
        """Deletes records older than X days."""
        query = """
        DELETE FROM job_snapshots 
        WHERE scraped_at < datetime('now', ?)
        """
        # SQLite datetime strings allow '-30 days' format
        self.conn.execute(query, (f'-{days} days',))
        self.conn.commit()