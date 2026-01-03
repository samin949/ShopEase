# check_db.py
import sqlite3

conn = sqlite3.connect('shopease.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Try to find user table
user_tables = ['user', 'users', 'User', 'Users']
for table_name in user_tables:
    try:
        cursor.execute(f"SELECT * FROM {table_name};")
        users = cursor.fetchall()
        if users:
            print(f"\nUsers in '{table_name}' table:")
            print(f"Columns: {[description[0] for description in cursor.description]}")
            for user in users:
                print(user)
            break
    except:
        continue

conn.close()