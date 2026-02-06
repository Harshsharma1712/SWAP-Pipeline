import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import sqlite3
import os
from app.detection.hashers import hash_dataset


class SnapshotMixin:
    """
    Mixin class that adds snapshot functionality to existing storage classes.
    
    This integrates snapshots directly into the existing databases
    (static_data.db and dynamic_data.db) instead of creating a separate file.
    """

    def _create_snapshot_table(self):
        """Create the snapshots table in the existing database."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                data_json TEXT NOT NULL,
                item_count INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        # Index for faster lookups
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_source 
            ON snapshots(source_name, created_at DESC);
        """)
        self.conn.commit()

    def save_snapshot(
        self, 
        source_name: str, 
        data: List[Dict[str, Any]]
    ) -> int:
        """
        Save a snapshot of the current data.
        
        Args:
            source_name: Identifier for the data source
            data: The data to snapshot
            
        Returns:
            ID of the created snapshot
        """
        now = datetime.now(timezone.utc).isoformat()
        data_json = json.dumps(data, sort_keys=True, default=str)
        data_hash = hash_dataset(data)

        cursor = self.conn.execute(
            """
            INSERT INTO snapshots (source_name, data_hash, data_json, item_count, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_name, data_hash, data_json, len(data), now)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_latest_snapshot(self, source_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve the most recent snapshot for a source.
        
        Args:
            source_name: Identifier for the data source
            
        Returns:
            The snapshot data, or None if no snapshot exists
        """
        cursor = self.conn.execute(
            """
            SELECT data_json FROM snapshots 
            WHERE source_name = ? 
            ORDER BY created_at DESC 
            LIMIT 1
            """,
            (source_name,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def cleanup_old_snapshots(self, source_name: str, keep_count: int = 10):
        """
        Remove old snapshots, keeping only the most recent ones.
        
        Args:
            source_name: Identifier for the data source
            keep_count: Number of recent snapshots to keep
        """
        self.conn.execute(
            """
            DELETE FROM snapshots 
            WHERE source_name = ? 
            AND id NOT IN (
                SELECT id FROM snapshots 
                WHERE source_name = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            )
            """,
            (source_name, source_name, keep_count)
        )
        self.conn.commit()
