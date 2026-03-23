import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'food_db.sqlite')
schema_path = os.path.join(os.path.dirname(__file__), 'database.sql')

print("Fixing the users table schema...")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Drop the old users table so it's forced to rebuild
    cursor.execute("DROP TABLE IF EXISTS users;")
    
    # 2. Re-run the schema to recreate it with the 'username' column
    with open(schema_path, 'r') as f:
        schema = f.read()
        conn.executescript(schema)
        
    print("✅ Successfully recreated the 'users' table with the new 'username' column!")
    print("Your recipes and ratings data were kept safe.")
    
except Exception as e:
    print(f"❌ Error fixing database: {e}")
    print("Make sure your Flask server is STOPPED before running this script.")
finally:
    if 'conn' in locals():
        conn.close()