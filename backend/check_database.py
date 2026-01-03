# backend/check_database.py
import sqlite3
import os

def check_database():
    db_path = 'shopease.db'
    
    print("🔍 CHECKING DATABASE")
    print("=" * 70)
    
    # Check if file exists
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        print("   Location:", os.path.abspath(db_path))
        return
    
    print(f"✅ Database found: {os.path.abspath(db_path)}")
    print(f"   Size: {os.path.getsize(db_path)} bytes")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📋 TABLES ({len(tables)}):")
    for table in tables:
        print(f"  • {table}")
    
    # Check products table
    if 'products' in tables:
        print("\n📦 PRODUCTS TABLE:")
        
        # Get column info
        cursor.execute("PRAGMA table_info(products);")
        columns = cursor.fetchall()
        
        print("  Columns:")
        for col in columns:
            col_name, col_type = col[1], col[2]
            print(f"    - {col_name}: {col_type}")
        
        # Count products
        cursor.execute("SELECT COUNT(*) FROM products;")
        count = cursor.fetchone()[0]
        print(f"\n  Total products: {count}")
        
        if count > 0:
            # Show all products
            print(f"\n  ALL PRODUCTS:")
            print("  " + "="*85)
            print(f"  {'ID':<4} {'Name':<40} {'Category':<15} {'Price':<10} {'Rating':<8}")
            print("  " + "-"*85)
            
            cursor.execute("""
                SELECT id, name, category, price, rating 
                FROM products 
                ORDER BY id
            """)
            
            for row in cursor.fetchall():
                product_id, name, category, price, rating = row
                # Truncate long names
                display_name = name[:38] + ".." if len(name) > 40 else name
                print(f"  {product_id:<4} {display_name:<40} {category:<15} ${price:<9.2f} {rating:<8.1f}")
            
            # Check for "Midhat"
            print(f"\n  SEARCHING FOR 'Midhat':")
            cursor.execute("SELECT name FROM products WHERE name LIKE '%Midhat%'")
            midhat_results = cursor.fetchall()
            
            if midhat_results:
                print(f"  ✅ Found {len(midhat_results)} product(s) containing 'Midhat':")
                for result in midhat_results:
                    print(f"    - {result[0]}")
            else:
                print(f"  ❌ No products containing 'Midhat' found.")
                
                # Show what names ARE in database
                print(f"\n  Sample of product names:")
                cursor.execute("SELECT DISTINCT name FROM products LIMIT 10")
                for row in cursor.fetchall():
                    print(f"    - {row[0]}")
    else:
        print("\n❌ 'products' table not found in database!")
    
    conn.close()
    print("\n✅ Database check complete!")

if __name__ == '__main__':
    check_database()