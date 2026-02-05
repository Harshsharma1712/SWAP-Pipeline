import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.sqlite_static import SQLiteStorage

def clear_database():
    confirm = input("Are you sure you want to WIPE all job data? (y/n): ").lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return

    try:
        storage = SQLiteStorage()
        
        # 1. Run the deletions inside a transaction
        with storage.conn:
            storage.conn.execute("DELETE FROM job_snapshots")
            # This resets the ID counter
            storage.conn.execute("DELETE FROM sqlite_sequence WHERE name='job_snapshots'")
        
        # 2. Run VACUUM outside of any transaction
        # We set isolation_level to None to ensure we are in 'autocommit' mode
        old_isolation = storage.conn.isolation_level
        storage.conn.isolation_level = None 
        storage.conn.execute("VACUUM")
        storage.conn.isolation_level = old_isolation
            
        print("✅ Database cleared successfully and IDs reset.")
        
    except Exception as e:
        print(f"❌ Failed to clear database: {e}")

if __name__ == "__main__":
    clear_database()