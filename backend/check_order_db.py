# check_orders_schema.py
import sqlite3

conn = sqlite3.connect('shopease.db')
cursor = conn.cursor()

print("=== ORDERS TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(orders);")
columns = cursor.fetchall()
print("\nColumns in 'orders' table:")
print("ID | Name | Type | Not Null | Default | PK")
print("-" * 60)
for col in columns:
    print(f"{col[0]:2} | {col[1]:15} | {col[2]:15} | {col[3]:8} | {col[4] or '':8} | {col[5]}")
    
print("\n\n=== SAMPLE DATA IN ORDERS TABLE ===")
cursor.execute("SELECT * FROM orders LIMIT 5;")
orders = cursor.fetchall()
if orders:
    print(f"\nFound {len(orders)} order(s):")
    for order in orders:
        print(order)
else:
    print("No orders found in table")

print("\n\n=== ORDER_ITEMS TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(order_items);")
columns = cursor.fetchall()
print("\nColumns in 'order_items' table:")
print("ID | Name | Type | Not Null | Default | PK")
print("-" * 60)
for col in columns:
    print(f"{col[0]:2} | {col[1]:15} | {col[2]:15} | {col[3]:8} | {col[4] or '':8} | {col[5]}")

print("\n\n=== SAMPLE ORDER ITEMS ===")
cursor.execute("SELECT * FROM order_items LIMIT 10;")
items = cursor.fetchall()
if items:
    print(f"\nFound {len(items)} order item(s):")
    for item in items:
        print(item)
        
conn.close()