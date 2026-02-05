import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.sqlite_static import StaticStorage
from app.storage.sqlite_dynamic import DynamicStorage

def clear_database():
    print("\n--- Database Cleanup Tool ---")
    print("1. Clear Static Database (static_data.db)")
    print("2. Clear Dynamic Database (dynamic_data.db)")
    print("3. Clear BOTH")
    print("q. Quit")
    
    choice = input("\nSelect an option: ").strip().lower()

    if choice == 'q':
        return

    confirm = input("⚠️  Are you sure? This cannot be undone. (y/n): ").lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return

    try:
        if choice == '1':
            StaticStorage().clear_all_data("job_snapshots")
            print("✅ Static database cleared.")
            
        elif choice == '2':
            DynamicStorage().clear_all_data("dynamic_jobs")
            print("✅ Dynamic database cleared.")
            
        elif choice == '3':
            StaticStorage().clear_all_data("job_snapshots")
            DynamicStorage().clear_all_data("dynamic_jobs")
            print("✅ Both databases cleared successfully.")
            
        else:
            print("❌ Invalid selection.")

    except Exception as e:
        print(f"❌ Failed to clear database: {e}")

if __name__ == "__main__":
    clear_database()