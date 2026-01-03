# add_missing_columns.py
import sqlite3

def add_missing_columns():
    conn = sqlite3.connect('shopease.db')
    cursor = conn.cursor()
    
    print("Checking and adding missing columns to 'orders' table...")
    
    # Check current columns
    cursor.execute("PRAGMA table_info(orders);")
    existing_columns = [col[1] for col in cursor.fetchall()]
    print(f"Existing columns: {existing_columns}")
    
    # Add user_id if it doesn't exist
    if 'user_id' not in existing_columns:
        print("Adding 'user_id' column...")
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN user_id INTEGER")
            print("✓ Added 'user_id' column")
        except Exception as e:
            print(f"Error adding user_id: {e}")
    
    # Add shipping_info if it doesn't exist
    if 'shipping_info' not in existing_columns:
        print("Adding 'shipping_info' column...")
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN shipping_info TEXT")
            print("✓ Added 'shipping_info' column")
        except Exception as e:
            print(f"Error adding shipping_info: {e}")
    
    conn.commit()
    
    # Verify changes
    cursor.execute("PRAGMA table_info(orders);")
    updated_columns = [col[1] for col in cursor.fetchall()]
    print(f"\nUpdated columns: {updated_columns}")
    
    conn.close()
    print("\n✅ Database updated successfully!")

if __name__ == "__main__":
    add_missing_columns()