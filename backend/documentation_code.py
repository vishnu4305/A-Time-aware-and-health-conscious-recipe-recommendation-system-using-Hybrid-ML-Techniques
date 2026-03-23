# PROJECT TITLE:
# Health-and-Time-aware-Food-Recommendation-System
# Consolidated version for documentation and presentation.

# ===================================================================
# 1. IMPORT REQUIRED LIBRARIES
# ===================================================================
import sqlite3
import os
import sys
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

# ===================================================================
# 2. INITIALIZATION AND CONFIGURATION
# ===================================================================

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Global variables to hold ML data
recipes_df = None
ratings_df = None


# ===================================================================
# 3. DATABASE MODULE
# ===================================================================

def get_db_connection():
    """
    Create and return a SQLite database connection.
    """
    try:
        # Get database path from .env or use default
        db_path = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'food_db.sqlite'))
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        return connection
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    Execute a SQL query.
    
    Args:
        query (str): SQL query string.
        params (tuple or dict): Query parameters.
        fetch (bool): If True, return fetched results.
        fetch_one (bool): If True, return only one result.
    
    Returns:
        Query results if fetch=True, otherwise a dict with affected_rows and last_id.
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if fetch:
            if fetch_one:
                row = cursor.fetchone()
                result = dict(row) if row else None
            else:
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
            return result
        else:
            connection.commit()
            affected_rows = cursor.rowcount
            last_id = cursor.lastrowid
            return {'affected_rows': affected_rows, 'last_id': last_id}
    except Exception as e:
        print(f"Error executing query: {e}")
        connection.rollback()
        return None
    finally:
        if connection:
            connection.close()


def initialize_database():
    """Create database tables if they don't exist."""
    print("Initializing database schema...")
    schema_queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            gender TEXT,
            activity_level REAL,
            conditions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            meal_type TEXT,
            dietary_restrictions TEXT,
            ingredients TEXT,
            instructions TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recipe_id INTEGER,
            rating INTEGER,
            timestamp TIMESTAMP,
            month_index INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id),
            UNIQUE (user_id, recipe_id)
        );
        """
    ]
    for query in schema_queries:
        execute_query(query)
    print("Database initialized successfully.")


def get_user_by_username(username):
    """Get user by username"""
    query = "SELECT * FROM users WHERE username = ?"
    return execute_query(query, (username,), fetch=True, fetch_one=True)


def get_user_by_id(user_id):
    """Get user by ID"""
    query = "SELECT * FROM users WHERE id = ?"
    return execute_query(query, (user_id,), fetch=True, fetch_one=True)


def create_user(username, name, age, height, weight, gender, conditions, activity_level=1.2):
    """Create a new user"""
    query = """
        INSERT INTO users (username, name, age, height, weight, gender, activity_level, conditions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    conditions_json = json.dumps(conditions) if conditions else json.dumps([])
    result = execute_query(query, (username, name, age, height, weight, gender, activity_level, conditions_json))
    return result['last_id'] if result else None


def update_user(user_id, name, age, height, weight, gender, conditions, activity_level=1.2):
    """Update an existing user"""
    query = """
        UPDATE users 
        SET name = ?, age = ?, height = ?, weight = ?, gender = ?, activity_level = ?, conditions = ?
        WHERE id = ?
    """
    conditions_json = json.dumps(conditions) if conditions else json.dumps([])
    return execute_query(query, (name, age, height, weight, gender, activity_level, conditions_json, user_id))


def get_all_recipes():
    """Get all recipes"""
    query = "SELECT * FROM recipes"
    return execute_query(query, fetch=True)


def get_recipe_by_id(recipe_id):
    """Get recipe by ID"""
    query = "SELECT * FROM recipes WHERE id = ?"
    return execute_query(query, (recipe_id,), fetch=True, fetch_one=True)


def get_all_ratings():
    """Get all ratings"""
    query = "SELECT * FROM ratings"
    return execute_query(query, fetch=True)


def get_user_ratings(user_id):
    """Get ratings for a specific user"""
    query = "SELECT * FROM ratings WHERE user_id = ?"
    return execute_query(query, (user_id,), fetch=True)


def add_rating(user_id, recipe_id, rating, timestamp, month_index):
    """Add or update a rating"""
    query = """
        INSERT INTO ratings (user_id, recipe_id, rating, timestamp, month_index)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, recipe_id) 
        DO UPDATE SET rating = ?, timestamp = ?, month_index = ?
    """
    return execute_query(query, (user_id, recipe_id, rating, timestamp, month_index, 
                                  rating, timestamp, month_index))


# ===================================================================
# 4. ML RECOMMENDER MODULE (PLACEHOLDERS)
# ===================================================================

def load_data():
    """
    Placeholder function to load recipe and rating data.
    In a real scenario, this would load data from CSVs or a database into pandas DataFrames.
    """
    global recipes_df, ratings_df
    print("Loading recipe and ratings data (using placeholder data)...")
    recipes_data = get_all_recipes()
    ratings_data = get_all_ratings()
    
    if recipes_data:
        recipes_df = pd.DataFrame(recipes_data)
    else:
        recipes_df = pd.DataFrame(columns=['id', 'name', 'meal_type'])
        
    if ratings_data:
        ratings_df = pd.DataFrame(ratings_data)
    else:
        ratings_df = pd.DataFrame(columns=['user_id', 'recipe_id', 'rating'])
        
    print(f"Data loaded: {len(recipes_df)} recipes, {len(ratings_df)} ratings.")


def get_recommendations(user_id, gamma, lambda_decay, top_n):
    """
    Placeholder for the main recommendation function.
    Returns a list of recommended recipes.
    """
    print(f"Generating {top_n} recommendations for user {user_id} with gamma={gamma}, lambda_decay={lambda_decay}")
    # In a real implementation, this would involve complex collaborative filtering,
    # content-based filtering, and time-decay calculations.
    all_recipes = get_all_recipes()
    if not all_recipes:
        return []
    
    # Return a random sample of recipes as a placeholder
    sample_size = min(top_n, len(all_recipes))
    recommended_indices = np.random.choice(len(all_recipes), sample_size, replace=False)
    recommendations = [all_recipes[i] for i in recommended_indices]
    return recommendations


def get_meal_plan_recommendations(user_id, gamma, lambda_decay, recipes_per_meal):
    """
    Placeholder for the meal plan recommendation function.
    Returns recipes organized by meal type.
    """
    print(f"Generating meal plan for user {user_id} with {recipes_per_meal} recipes per meal.")
    meal_plan = {
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snacks": []
    }
    all_recipes = get_all_recipes()
    if not all_recipes:
        return meal_plan

    # Simple placeholder logic: randomly assign recipes to meal types
    for meal_type in meal_plan.keys():
        # Filter recipes by meal type (case-insensitive)
        type_recipes = [r for r in all_recipes if r['meal_type'] and meal_type.lower() in r['meal_type'].lower()]
        if not type_recipes:
            type_recipes = all_recipes # Fallback to all recipes
        
        sample_size = min(recipes_per_meal, len(type_recipes))
        recommended_indices = np.random.choice(len(type_recipes), sample_size, replace=False)
        meal_plan[meal_type] = [type_recipes[i] for i in recommended_indices]
        
    return meal_plan


# ===================================================================
# 5. FLASK BACKEND API ROUTES
# ===================================================================

# --- User Routes ---
@app.route('/user/create', methods=['POST'])
def create_user_route():
    try:
        data = request.json
        if not all(k in data for k in ['username', 'name', 'age', 'height', 'weight']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        existing_user = get_user_by_username(data['username'])
        if existing_user:
            return jsonify({'error': 'Username already exists. Please choose another one.'}), 409
        
        user_id = create_user(
            username=data['username'], name=data['name'], age=data['age'], height=data['height'], weight=data['weight'],
            gender=data.get('gender', 'male'), conditions=data.get('conditions', []),
            activity_level=data.get('activity_level', 1.2)
        )
        
        if user_id:
            user = get_user_by_id(user_id)
            return jsonify({'message': 'User created successfully', 'user_id': user_id, 'user': user}), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_route(user_id):
    user = get_user_by_id(user_id)
    return (jsonify(user), 200) if user else (jsonify({'error': 'User not found'}), 404)

@app.route('/user/by-username/<username>', methods=['GET'])
def get_user_by_username_route(username):
    user = get_user_by_username(username)
    return (jsonify(user), 200) if user else (jsonify({'error': 'User not found'}), 404)


@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user_route_doc(user_id):
    try:
        data = request.json
        if not all(k in data for k in ['name', 'age', 'height', 'weight']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        update_user(
            user_id=user_id, name=data['name'], age=data['age'], height=data['height'], weight=data['weight'],
            gender=data.get('gender', 'male'), conditions=data.get('conditions', []),
            activity_level=data.get('activity_level', 1.2)
        )
        user = get_user_by_id(user_id)
        return jsonify({'message': 'User updated successfully', 'user': user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Recipe Routes ---
@app.route('/recipes', methods=['GET'])
def get_recipes_route():
    limit = request.args.get('limit', type=int)
    recipes = get_all_recipes()
    if limit and recipes:
        recipes = recipes[:limit]
    return jsonify(recipes), 200

@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe_route(recipe_id):
    recipe = get_recipe_by_id(recipe_id)
    return (jsonify(recipe), 200) if recipe else (jsonify({'error': 'Recipe not found'}), 404)

# --- Recommendation Routes ---
@app.route('/recommend', methods=['POST'])
def recommend_route():
    try:
        data = request.json
        user_id = data.get('user_id')
        if not user_id or not get_user_by_id(user_id):
            return jsonify({'error': 'Valid user_id is required'}), 400
        
        recommendations = get_recommendations(
            user_id=user_id,
            gamma=float(data.get('gamma', 0.5)),
            lambda_decay=float(data.get('lambda_decay', 2.5)),
            top_n=int(data.get('top_n', 10))
        )
        return jsonify({'user_id': user_id, 'recommendations': recommendations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommend/meal-plan', methods=['POST'])
def recommend_meal_plan_route():
    try:
        data = request.json
        user_id = data.get('user_id')
        if not user_id or not get_user_by_id(user_id):
            return jsonify({'error': 'Valid user_id is required'}), 400

        meal_plan = get_meal_plan_recommendations(
            user_id=user_id,
            gamma=float(data.get('gamma', 0.5)),
            lambda_decay=float(data.get('lambda_decay', 2.5)),
            recipes_per_meal=int(data.get('recipes_per_meal', 3))
        )
        return jsonify(meal_plan), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# --- Rating Routes ---
@app.route('/rate', methods=['POST'])
def rate_recipe_route():
    try:
        data = request.json
        user_id, recipe_id, rating = data.get('user_id'), data.get('recipe_id'), data.get('rating')

        if not all([user_id, recipe_id, rating]):
            return jsonify({'error': 'Missing required fields'}), 400
        if not (get_user_by_id(user_id) and get_recipe_by_id(recipe_id)):
            return jsonify({'error': 'User or Recipe not found'}), 404

        timestamp = datetime.now()
        all_ratings = get_all_ratings()
        if all_ratings:
            min_ts_str = min(r['timestamp'] for r in all_ratings if r['timestamp'])
            min_timestamp = datetime.fromisoformat(min_ts_str.replace('Z', '+00:00'))
            month_index = (timestamp.year - min_timestamp.year) * 12 + (timestamp.month - min_timestamp.month) + 1
        else:
            month_index = 1
        
        result = add_rating(user_id, recipe_id, rating, timestamp, month_index)
        if result:
            return jsonify({'message': 'Rating saved successfully'}), 201
        else:
            return jsonify({'error': 'Failed to save rating'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ratings/<int:user_id>', methods=['GET'])
def get_user_ratings_route(user_id):
    ratings = get_user_ratings(user_id)
    return jsonify(ratings), 200

# --- Health Check Route ---
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200


# ===================================================================
# 6. MAIN EXECUTION
# ===================================================================

if __name__ == '__main__':
    # Ensure database and tables exist before starting the app
    initialize_database()
    
    # Load ML data into memory
    load_data()
    
    # Run the Flask application
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
