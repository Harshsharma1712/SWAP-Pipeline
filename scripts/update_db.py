import sqlite3
import os
import sys

def update_job_title(job_id, new_title):
    # Absolute pathing logic to find /data/static_data.db
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.normpath(os.path.join(base_path, "..", "data", "static_data.db"))

    if not os.path.exists(db_path):
        print(f"❌ Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Using placeholders (?) to prevent SQL Injection
        sql = "UPDATE job_snapshots SET title = ? WHERE id = ?"
        cursor.execute(sql, (new_title, job_id))

        if cursor.rowcount == 0:
            print(f"⚠️ No record found with ID: {job_id}")
        else:
            conn.commit()
            print(f"✅ Success: ID {job_id} updated to '{new_title}'")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # sys.argv[0] is the script name
    # sys.argv[1] is the first argument (ID)
    # sys.argv[2] is the second argument (Title)
    
    if len(sys.argv) == 3:
        target_id = sys.argv[1]
        target_title = sys.argv[2]
        update_job_title(target_id, target_title)
    else:
        print("Usage: python scripts/update_db.py <id> <new_title>")
        print("Example: python scripts/update_db.py 1 'Full Stack Developer'")