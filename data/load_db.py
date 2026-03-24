"""
Load processed data into SQLite database
"""
import pandas as pd
from pymongo import MongoClient
import os
import sys
from dotenv import load_dotenv

# Load environment variables from backend
backend_env = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(backend_env)


def get_db():
    """Create MongoDB connection"""
    try:
        # Temporarily hardcode the URI to guarantee it is read correctly
        mongo_uri = "mongodb+srv://vishnu123:A.vishnu%40123@cluster0.1iu5btx.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(mongo_uri)
        db = client['food_recommendation']
        
        # Test connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None


def load_recipes(db, file_path='processed/recipes_processed.csv'):
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
    
    # Target collection
    collection = db.recipes
    print("Clearing existing recipes...")
    collection.delete_many({})
    
    # Insert in batches
    batch_size = 1000
    total = len(recipes_df)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = recipes_df.iloc[i:i+batch_size]
        
        documents = []
        for _, row in batch.iterrows():
            documents.append({
                '_id': int(row['id']),
                'name': str(row['name'])[:255],
                'ingredients': str(row['ingredients']),
                'calories': int(row['calories']) if pd.notna(row['calories']) else 0,
                'protein': float(row['protein']) if pd.notna(row['protein']) else 0.0,
                'fat': float(row['fat']) if pd.notna(row['fat']) else 0.0,
                'carbs': float(row['carbs']) if pd.notna(row['carbs']) else 0.0,
                'sugar': float(row['sugar']) if pd.notna(row['sugar']) else 0.0,
                'sodium': float(row['sodium']) if pd.notna(row['sodium']) else 0.0,
                'gl': float(row['gl']) if pd.notna(row['gl']) else 0.0,
                'steps': str(row['steps']) if pd.notna(row['steps']) else '',
                'image_url': str(row['image_url'])[:500] if pd.notna(row['image_url']) else ''
            })
        
        try:
            if documents:
                collection.insert_many(documents, ordered=False)
                inserted += len(documents)
            print(f"Progress: {inserted}/{total} recipes loaded ({(inserted/total)*100:.1f}%)")
        except Exception as e:
            # ordered=False allows continuing on duplicate key errors
            print(f"Error in batch: {e}")
            
    print(f"✓ Successfully loaded {inserted} recipes")
    return True


def load_ratings(db, file_path='processed/ratings_processed.csv'):
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
    
    # Target collection
    collection = db.ratings
    print("Clearing existing ratings...")
    collection.delete_many({})
    
    # Create compound index for fast queries
    collection.create_index([("user_id", 1), ("recipe_id", 1)], unique=True)
    
    # Insert in batches
    batch_size = 5000
    total = len(ratings_df)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = ratings_df.iloc[i:i+batch_size]
        
        documents = []
        for _, row in batch.iterrows():
            documents.append({
                'user_id': int(row['user_id']),
                'recipe_id': int(row['recipe_id']),
                'rating': int(row['rating']),
                'timestamp': pd.to_datetime(row['timestamp']).isoformat(),
                'month_index': int(row['month_index'])
            })
        
        try:
            if documents:
                collection.insert_many(documents, ordered=False)
                inserted += len(documents)
            print(f"Progress: {inserted}/{total} ratings loaded ({(inserted/total)*100:.1f}%)")
        except Exception as e:
            pass # ordered=False continues on duplicates
    print(f"✓ Successfully loaded {inserted} ratings")
    return True


def verify_data(db):
    """
    Verify loaded data
    """
    print("\n" + "=" * 60)
    print("Verifying Database")
    print("=" * 60)
    
    # Count recipes
    recipe_count = db.recipes.count_documents({})
    print(f"✓ Recipes in database: {recipe_count}")
    
    # Count ratings
    rating_count = db.ratings.count_documents({})
    print(f"✓ Ratings in database: {rating_count}")
    
    # Count unique users in ratings
    user_count = len(db.ratings.distinct('user_id'))
    print(f"✓ Unique users with ratings: {user_count}")
    
    # Get sample recipe
    sample = db.recipes.find_one()
    if sample:
        print(f"\nSample Recipe:")
        print(f"  Name: {sample.get('name')}")
        print(f"  Calories: {sample.get('calories')}, Protein: {sample.get('protein')}")


def main():
    """
    Main function to load all data
    """
    print("=" * 60)
    print("Loading Food.com Data into MongoDB")
    print("=" * 60)
    
    # Check if database exists
    db = get_db()
    
    if db is None:
        print("\nERROR: Could not connect to database!")
        return
    
    try:
        # Load recipes
        print("\n" + "=" * 60)
        print("Step 1: Loading Recipes")
        print("=" * 60)
        if not load_recipes(db):
            print("Failed to load recipes")
            return
        
        # Load ratings
        print("\n" + "=" * 60)
        print("Step 2: Loading Ratings")
        print("=" * 60)
        if not load_ratings(db):
            print("Failed to load ratings")
            return
        
        # Verify
        verify_data(db)
        
        print("\n" + "=" * 60)
        print("✓ Data Loading Complete!")
        print("=" * 60)
        print("You can now start the backend server (python app.py)")
        
    finally:
        print("\nProcess finished.")


if __name__ == '__main__':
    main()
