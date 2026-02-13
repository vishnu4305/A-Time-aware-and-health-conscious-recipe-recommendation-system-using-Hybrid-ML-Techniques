"""
Script to add gender column to users table
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('food_db.sqlite')
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'gender' not in columns:
        print("Adding gender column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'male'")
        conn.commit()
        print("✅ Gender column added successfully!")
    else:
        print("✅ Gender column already exists!")
    
    # Verify
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nCurrent columns in users table: {columns}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n✅ Database update complete!")
