import sqlite3
import os

class BaseStorage:
    def __init__(self, db_path: str):
        # Ensure the data folder exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def clear_all_data(self, table_name: str):
        """Optimized wipe for any specific table."""
        try:
            # 1. Delete data & reset ID counter
            self.conn.execute(f"DELETE FROM {table_name}")
            self.conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
            self.conn.commit()
            
            # 2. Optimized VACUUM (must be outside transaction)
            old_level = self.conn.isolation_level
            self.conn.isolation_level = None
            self.conn.execute("VACUUM")
            self.conn.isolation_level = old_level
            print(f"✅ {table_name} cleared and storage optimized.")
        except sqlite3.Error as e:
            print(f"❌ Error clearing table: {e}")