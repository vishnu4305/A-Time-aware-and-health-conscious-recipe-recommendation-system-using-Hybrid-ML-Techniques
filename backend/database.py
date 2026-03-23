"""
Database connection module for SQLite
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """
    Create and return a SQLite database connection
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
    Execute a SQL query
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        fetch: If True, return fetched results
        fetch_one: If True, return only one result
    
    Returns:
        Query results if fetch=True, otherwise number of affected rows
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
            cursor.close()
            connection.close()
            return result
        else:
            connection.commit()
            affected_rows = cursor.rowcount
            last_id = cursor.lastrowid
            cursor.close()
            connection.close()
            return {'affected_rows': affected_rows, 'last_id': last_id}
    except Exception as e:
        print(f"Error executing query: {e}")
        connection.rollback()
        connection.close()
        return None


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
    import json
    query = """
        INSERT INTO users (username, name, age, height, weight, gender, activity_level, conditions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    conditions_json = json.dumps(conditions) if conditions else json.dumps([])
    result = execute_query(query, (username, name, age, height, weight, gender, activity_level, conditions_json))
    return result['last_id'] if result else None


def update_user(user_id, name, age, height, weight, gender, conditions, activity_level=1.2):
    """Update an existing user"""
    import json
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


def get_rating_count():
    """Get total count of ratings (fast query for cache checking)"""
    query = "SELECT COUNT(*) as count FROM ratings"
    result = execute_query(query, fetch=True, fetch_one=True)
    return result['count'] if result else 0


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
