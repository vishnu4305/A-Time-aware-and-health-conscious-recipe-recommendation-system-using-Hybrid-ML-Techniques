"""
Test script to verify SQLite database connection and basic operations
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import database as db

print("=" * 60)
print("Testing SQLite Database Connection")
print("=" * 60)

# Test connection
print("\n1. Testing database connection...")
connection = db.get_db_connection()
if connection:
    print("✓ Successfully connected to SQLite database")
    connection.close()
else:
    print("✗ Failed to connect to database")
    sys.exit(1)

# Test creating a user
print("\n2. Testing user creation...")
user_id = db.create_user(
    name="Test User",
    age=25,
    height=170,
    weight=70,
    conditions=["diabetes"],
    activity_level=1.55
)
if user_id:
    print(f"✓ User created successfully with ID: {user_id}")
else:
    print("✗ Failed to create user")

# Test retrieving user
print("\n3. Testing user retrieval...")
user = db.get_user_by_id(user_id)
if user:
    print(f"✓ Retrieved user: {user['name']}, Age: {user['age']}")
else:
    print("✗ Failed to retrieve user")

# Test recipe count
print("\n4. Testing recipe retrieval...")
recipes = db.get_all_recipes()
if recipes:
    print(f"✓ Found {len(recipes)} recipes in database")
    if len(recipes) > 0:
        print(f"  Sample recipe: {recipes[0]['name']}")
else:
    print("⚠ No recipes found (database might be empty)")
    print("  Run 'python data/load_db.py' to load data")

# Test rating count
print("\n5. Testing rating retrieval...")
ratings = db.get_all_ratings()
if ratings:
    print(f"✓ Found {len(ratings)} ratings in database")
else:
    print("⚠ No ratings found (database might be empty)")

print("\n" + "=" * 60)
print("Database Test Complete!")
print("=" * 60)
print("\nIf you see '✓' marks above, your SQLite setup is working correctly!")
print("\nNext steps:")
print("1. Download dataset from Kaggle")
print("2. Run: python data/preprocess.py")
print("3. Run: python data/load_db.py")
print("4. Run: python backend/app.py")
