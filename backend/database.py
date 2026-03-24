"""
Database connection module for MongoDB
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = None
db_instance = None

def get_db():
    """
    Create and return a MongoDB connection
    """
    global client, db_instance
    if db_instance is None:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        try:
            client = MongoClient(mongo_uri)
            db_instance = client['food_recommendation']
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
    return db_instance

def get_next_sequence_value(sequence_name):
    """Helper for auto-incrementing integer IDs in MongoDB to maintain ML model compatibility"""
    database = get_db()
    try:
        counter = database.counters.find_one_and_update(
            {'_id': sequence_name},
            {'$inc': {'sequence_value': 1}},
            upsert=True,
            return_document=True
        )
        return counter['sequence_value']
    except:
        import random
        return random.randint(1000, 999999)


def get_user_by_username(username):
    """Get user by username"""
    database = get_db()
    user = database.users.find_one({'username': username})
    if user:
        user['id'] = user.get('_id')
    return user


def get_user_by_id(user_id):
    """Get user by ID"""
    database = get_db()
    user = database.users.find_one({'_id': user_id})
    if user:
        user['id'] = user.get('_id')
    return user


def create_user(username, name, age, height, weight, gender, conditions, activity_level=1.2):
    """Create a new user"""
    database = get_db()
    user_id = get_next_sequence_value('userid')
    user = {
        '_id': user_id,
        'username': username,
        'name': name,
        'age': age,
        'height': height,
        'weight': weight,
        'gender': gender,
        'activity_level': activity_level,
        'conditions': conditions if conditions else []
    }
    database.users.insert_one(user)
    return user_id


def update_user(user_id, name, age, height, weight, gender, conditions, activity_level=1.2):
    """Update an existing user"""
    database = get_db()
    database.users.update_one(
        {'_id': user_id},
        {'$set': {
            'name': name,
            'age': age,
            'height': height,
            'weight': weight,
            'gender': gender,
            'activity_level': activity_level,
            'conditions': conditions if conditions else []
        }}
    )
    return {'affected_rows': 1}


def get_all_recipes(limit=None):
    """Get all recipes"""
    database = get_db()
    cursor = database.recipes.find()
    if limit:
        cursor = cursor.limit(limit)
    
    recipes = list(cursor)
    for r in recipes:
        r['id'] = r.pop('_id', r.get('id'))
    return recipes


def get_recipe_by_id(recipe_id):
    """Get recipe by ID"""
    database = get_db()
    recipe = database.recipes.find_one({'_id': recipe_id})
    if recipe:
        recipe['id'] = recipe.pop('_id', recipe.get('id'))
    return recipe


def get_all_ratings(limit=None):
    """Get all ratings"""
    database = get_db()
    cursor = database.ratings.find()
    if limit:
        cursor = cursor.limit(limit)
        
    ratings = list(cursor)
    for r in ratings:
        r['id'] = r.get('_id')
    return ratings


def get_rating_count():
    """Get total count of ratings (fast query for cache checking)"""
    database = get_db()
    return database.ratings.count_documents({})


def get_user_ratings(user_id):
    """Get ratings for a specific user"""
    database = get_db()
    ratings = list(database.ratings.find({'user_id': user_id}))
    for r in ratings:
        r['id'] = r.get('_id')
    return ratings


def add_rating(user_id, recipe_id, rating, timestamp, month_index):
    """Add or update a rating"""
    database = get_db()
    timestamp_str = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else timestamp
    database.ratings.update_one(
        {'user_id': user_id, 'recipe_id': recipe_id},
        {'$set': {
            'rating': rating,
            'timestamp': timestamp_str,
            'month_index': month_index
        }},
        upsert=True
    )
    return {'affected_rows': 1}


def get_earliest_rating_timestamp():
    """Get the earliest timestamp to calculate month_index"""
    database = get_db()
    earliest = database.ratings.find_one(sort=[("timestamp", 1)])
    if earliest:
        return earliest.get('timestamp')
    return None


def get_random_recipes(limit=10):
    """Get a random selection of recipes for cold start fallbacks"""
    database = get_db()
    pipeline = [{'$match': {'ingredients': {'$ne': None}}}, {'$sample': {'size': limit}}]
    recipes = list(database.recipes.aggregate(pipeline))
    for r in recipes:
        r['id'] = r.pop('_id', r.get('id'))
    return recipes


def get_recipes_with_offset(skip_amount, limit_amount):
    """Get recipes with pagination/offset for meal plan fallbacks"""
    database = get_db()
    recipes = list(database.recipes.find().skip(skip_amount).limit(limit_amount))
    for r in recipes:
        r['id'] = r.pop('_id', r.get('id'))
    return recipes
