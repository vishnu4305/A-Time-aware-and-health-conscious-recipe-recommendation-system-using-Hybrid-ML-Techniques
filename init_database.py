"""
Initialize SQLite database with tables
Run this before loading data
"""
import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'food_db.sqlite')
schema_path = os.path.join(os.path.dirname(__file__), 'database.sql')

print("=" * 60)
print("Initializing SQLite Database")
print("=" * 60)
print(f"Database location: {db_path}\n")

# Create connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Read and execute schema
with open(schema_path, 'r') as f:
    schema = f.read()
    conn.executescript(schema)

print("✓ Database tables created successfully!")

# Verify tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nCreated tables:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()

print("\n" + "=" * 60)
print("Database initialization complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Download dataset from Kaggle")
print("2. Place RAW_recipes.csv and RAW_interactions.csv in data/ folder")
print("3. Run: python data/preprocess.py")
print("4. Run: python data/load_db.py")
