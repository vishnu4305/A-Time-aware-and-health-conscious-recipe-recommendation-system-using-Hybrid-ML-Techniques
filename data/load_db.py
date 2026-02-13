"""
Load processed data into SQLite database
"""
import pandas as pd
import sqlite3
import os
import sys
from dotenv import load_dotenv

# Load environment variables from backend
backend_env = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(backend_env)


def get_db_connection():
    """Create SQLite connection"""
    try:
        # Get database path from .env or use default
        db_path = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'food_db.sqlite'))
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        
        connection = sqlite3.connect(db_path)
        print(f"Successfully connected to SQLite database at {db_path}")
        return connection
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None


def load_recipes(connection, file_path='processed/recipes_processed.csv'):
    """
    Load recipes into database
    """
    print(f"\nLoading recipes from {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"ERROR: {file_path} not found!")
        print("Please run preprocess.py first")
        return False
    
    # Read CSV
    recipes_df = pd.read_csv(file_path)
    print(f"Found {len(recipes_df)} recipes")
    
    # Prepare INSERT query
    cursor = connection.cursor()
    
    insert_query = """
        INSERT OR REPLACE INTO recipes (id, name, ingredients, calories, protein, fat, carbs, sugar, sodium, gl, steps, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Insert in batches
    batch_size = 1000
    total = len(recipes_df)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = recipes_df.iloc[i:i+batch_size]
        
        values = []
        for _, row in batch.iterrows():
            values.append((
                int(row['id']),
                str(row['name'])[:255],  # Limit to 255 chars
                str(row['ingredients'])[:65535],  # TEXT limit
                int(row['calories']) if pd.notna(row['calories']) else 0,
                float(row['protein']) if pd.notna(row['protein']) else 0.0,
                float(row['fat']) if pd.notna(row['fat']) else 0.0,
                float(row['carbs']) if pd.notna(row['carbs']) else 0.0,
                float(row['sugar']) if pd.notna(row['sugar']) else 0.0,
                float(row['sodium']) if pd.notna(row['sodium']) else 0.0,
                float(row['gl']) if pd.notna(row['gl']) else 0.0,
                str(row['steps'])[:65535] if pd.notna(row['steps']) else '',
                str(row['image_url'])[:500] if pd.notna(row['image_url']) else ''
            ))
        
        try:
            cursor.executemany(insert_query, values)
            connection.commit()
            inserted += len(values)
            print(f"Progress: {inserted}/{total} recipes loaded ({(inserted/total)*100:.1f}%)")
        except Exception as e:
            print(f"Error inserting batch: {e}")
            connection.rollback()
    
    cursor.close()
    print(f"✓ Successfully loaded {inserted} recipes")
    return True


def load_ratings(connection, file_path='processed/ratings_processed.csv'):
    """
    Load ratings into database
    """
    print(f"\nLoading ratings from {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"ERROR: {file_path} not found!")
        print("Please run preprocess.py first")
        return False
    
    # Read CSV
    ratings_df = pd.read_csv(file_path)
    print(f"Found {len(ratings_df)} ratings")
    
    # Prepare INSERT query
    cursor = connection.cursor()
    
    insert_query = """
        INSERT OR REPLACE INTO ratings (user_id, recipe_id, rating, timestamp, month_index)
        VALUES (?, ?, ?, ?, ?)
    """
    
    # Insert in batches
    batch_size = 5000
    total = len(ratings_df)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = ratings_df.iloc[i:i+batch_size]
        
        values = []
        for _, row in batch.iterrows():
            values.append((
                int(row['user_id']),
                int(row['recipe_id']),
                int(row['rating']),
                pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                int(row['month_index'])
            ))
        
        try:
            cursor.executemany(insert_query, values)
            connection.commit()
            inserted += len(values)
            print(f"Progress: {inserted}/{total} ratings loaded ({(inserted/total)*100:.1f}%)")
        except Exception as e:
            print(f"Error inserting batch: {e}")
            connection.rollback()
    
    cursor.close()
    print(f"✓ Successfully loaded {inserted} ratings")
    return True


def verify_data(connection):
    """
    Verify loaded data
    """
    print("\n" + "=" * 60)
    print("Verifying Database")
    print("=" * 60)
    
    cursor = connection.cursor()
    
    # Count recipes
    cursor.execute("SELECT COUNT(*) FROM recipes")
    recipe_count = cursor.fetchone()[0]
    print(f"✓ Recipes in database: {recipe_count}")
    
    # Count ratings
    cursor.execute("SELECT COUNT(*) FROM ratings")
    rating_count = cursor.fetchone()[0]
    print(f"✓ Ratings in database: {rating_count}")
    
    # Count unique users in ratings
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM ratings")
    user_count = cursor.fetchone()[0]
    print(f"✓ Unique users with ratings: {user_count}")
    
    # Get sample recipe
    cursor.execute("SELECT name, calories, protein, fat, carbs FROM recipes LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        print(f"\nSample Recipe:")
        print(f"  Name: {sample[0]}")
        print(f"  Calories: {sample[1]}, Protein: {sample[2]}, Fat: {sample[3]}, Carbs: {sample[4]}")
    
    cursor.close()


def main():
    """
    Main function to load all data
    """
    print("=" * 60)
    print("Loading Food.com Data into SQLite")
    print("=" * 60)
    
    # Check if database exists
    connection = get_db_connection()
    
    if not connection:
        print("\nERROR: Could not connect to database!")
        print("Please ensure:")
        print("1. Backend .env file has correct DATABASE_PATH")
        print("2. Run database.sql first to create tables")
        return
    
    # Create tables first
    print("\n" + "=" * 60)
    print("Creating Database Tables")
    print("=" * 60)
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'database.sql'), 'r') as f:
            schema_sql = f.read()
            connection.executescript(schema_sql)
            print("✓ Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return
    
    try:
        # Load recipes
        print("\n" + "=" * 60)
        print("Step 1: Loading Recipes")
        print("=" * 60)
        if not load_recipes(connection):
            print("Failed to load recipes")
            return
        
        # Load ratings
        print("\n" + "=" * 60)
        print("Step 2: Loading Ratings")
        print("=" * 60)
        if not load_ratings(connection):
            print("Failed to load ratings")
            return
        
        # Verify
        verify_data(connection)
        
        print("\n" + "=" * 60)
        print("✓ Data Loading Complete!")
        print("=" * 60)
        print("You can now start the backend server (python app.py)")
        
    finally:
        connection.close()
        print("\nDatabase connection closed")


if __name__ == '__main__':
    main()
