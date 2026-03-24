"""

Time-Aware Health-Conscious Recipe Recommendation System
Flask Backend API

"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# Add ml_models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import database as db
from ml_models.recommender import get_recommendations, get_meal_plan_recommendations, load_data

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# ==================== Database Setup & Fix ====================
def initialize_and_fix_db():
    print("Checking database schema...")
    conn = db.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # 1. Run database.sql to ensure all tables exist
            schema_path = os.path.join(os.path.dirname(__file__), '..', 'database.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
            
            # 2. Check if the username column exists in users table
            cursor.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if columns and ('username' not in columns or 'gender' not in columns):
                print("Missing username or gender column! Fixing users table...")
                cursor.execute("DROP TABLE IF EXISTS users")
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
                print("Users table fixed!")
                
            # 3. Add test recipes if the database is empty (Great for Render/Vercel demos)
            cursor.execute("SELECT COUNT(*) FROM recipes")
            count = cursor.fetchone()[0]
            if count == 0:
                print("Database is empty! Inserting demo recipes for the cloud deployment...")
                conn.executescript('''
                    INSERT OR IGNORE INTO recipes (id, name, meal_type, dietary_restrictions, ingredients, instructions, calories, protein, carbs, fat) VALUES 
                    (1, 'Healthy Grilled Chicken Salad', 'lunch, dinner', 'high-protein, low-carb', 'chicken breast, lettuce, tomatoes, cucumbers, olive oil', 'Grill the chicken. Chop vegetables. Toss with olive oil.', 350, 45, 10, 15),
                    (2, 'Oatmeal with Berries', 'breakfast', 'vegetarian, high-fiber', 'oats, milk, strawberries, blueberries, honey', 'Boil oats with milk. Top with fresh berries and honey.', 250, 8, 45, 4),
                    (3, 'Avocado Toast with Egg', 'breakfast, lunch', 'vegetarian', 'whole wheat bread, avocado, egg, salt, pepper', 'Toast bread. Mash avocado. Top with fried egg.', 320, 12, 20, 22),
                    (4, 'Baked Salmon with Asparagus', 'dinner', 'pescatarian, keto', 'salmon fillet, asparagus, lemon, garlic, butter', 'Bake salmon and asparagus at 400F for 15 mins.', 450, 35, 8, 28);
                ''')
                conn.commit()
                print("Demo recipes inserted successfully!")
        except Exception as e:
            print(f"Database setup error: {e}")
        finally:
            conn.close()

initialize_and_fix_db()

# Load data at startup
print("Loading recipe and ratings data...")
load_data()
print("Data loaded successfully!")


# ==================== User Routes ====================

@app.route('/user/create', methods=['POST'])
def create_user():
    """
    Create a new user profile
    
    Request JSON:
    {
        "username": "vishnu123",
        "name": "Vishnu",
        "age": 25,
        "height": 169,
        "weight": 80,
        "activity_level": 1.55,
        "conditions": ["diabetes"]
    }
    """
    try:
        data = request.json
        username = data.get('username')
        name = data.get('name')
        age = data.get('age')
        height = data.get('height')
        weight = data.get('weight')
        gender = data.get('gender', 'male')
        activity_level = data.get('activity_level', 1.2)
        conditions = data.get('conditions', [])
        
        # Validate required fields
        if not all([username, name, age, height, weight]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({'error': 'Username already exists. Please choose another one.'}), 409
        
        # Create new user
        user_id = db.create_user(username, name, age, height, weight, gender, conditions, activity_level)
        
        if user_id:
            user = db.get_user_by_id(user_id)
            return jsonify({
                'message': 'User created successfully',
                'user_id': user_id,
                'user': user
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user profile by ID
    """
    try:
        user = db.get_user_by_id(user_id)
        if user:
            return jsonify(user), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/user/by-username/<username>', methods=['GET'])
def get_user_by_username(username):
    """
    Get user profile by username
    """
    try:
        user = db.get_user_by_username(username)
        if user:
            return jsonify(user), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """
    Update an existing user profile
    """
    try:
        data = request.json
        name = data.get('name')
        age = data.get('age')
        height = data.get('height')
        weight = data.get('weight')
        gender = data.get('gender', 'male')
        activity_level = data.get('activity_level', 1.2)
        conditions = data.get('conditions', [])
        
        if not all([name, age, height, weight]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        db.update_user(user_id, name, age, height, weight, gender, conditions, activity_level)
        user = db.get_user_by_id(user_id)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Recipe Routes ====================

@app.route('/recipes', methods=['GET'])
def get_recipes():
    """
    Get all recipes (with optional limit)
    """
    try:
        limit = request.args.get('limit', type=int)
        recipes = db.get_all_recipes()
        
        if limit and recipes:
            recipes = recipes[:limit]
        
        return jsonify(recipes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """
    Get recipe details by ID
    """
    try:
        recipe = db.get_recipe_by_id(recipe_id)
        if recipe:
            return jsonify(recipe), 200
        else:
            return jsonify({'error': 'Recipe not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Recommendation Routes ====================

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Get personalized recipe recommendations
    
    Request JSON:
    {
        "user_id": 1,
        "gamma": 0.5,
        "lambda_decay": 2.5,
        "top_n": 10
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        gamma = float(data.get('gamma', 0.5))
        lambda_decay = float(data.get('lambda_decay', 2.5))
        top_n = int(data.get('top_n', 10))
        
        # Validate user_id
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Validate gamma (0-1)
        if not 0 <= gamma <= 1:
            return jsonify({'error': 'gamma must be between 0 and 1'}), 400
        
        # Validate lambda_decay (0.5-4)
        if not 0.5 <= lambda_decay <= 4:
            return jsonify({'error': 'lambda_decay must be between 0.5 and 4'}), 400
        
        # Check if user exists
        user = db.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recommendations
        recommendations = get_recommendations(user_id, gamma, lambda_decay, top_n)
        
        # FALLBACK for Cloud Deployments (if database is completely empty or read-only)
        if recommendations is None or len(recommendations) == 0:
            print("Database returned 0 recipes. Using fallback mock recipes...")
            recommendations = [
                {'id': 1, 'name': 'Healthy Grilled Chicken Salad', 'meal_type': 'lunch, dinner', 'dietary_restrictions': 'high-protein, low-carb', 'ingredients': 'chicken breast, lettuce, tomatoes, cucumbers, olive oil', 'instructions': 'Grill the chicken. Chop vegetables. Toss with olive oil.', 'calories': 350, 'protein': 45, 'carbs': 10, 'fat': 15},
                {'id': 2, 'name': 'Oatmeal with Berries', 'meal_type': 'breakfast', 'dietary_restrictions': 'vegetarian, high-fiber', 'ingredients': 'oats, milk, strawberries, blueberries, honey', 'instructions': 'Boil oats with milk. Top with fresh berries and honey.', 'calories': 250, 'protein': 8, 'carbs': 45, 'fat': 4},
                {'id': 3, 'name': 'Avocado Toast with Egg', 'meal_type': 'breakfast, lunch', 'dietary_restrictions': 'vegetarian', 'ingredients': 'whole wheat bread, avocado, egg, salt, pepper', 'instructions': 'Toast bread. Mash avocado. Top with fried egg.', 'calories': 320, 'protein': 12, 'carbs': 20, 'fat': 22},
                {'id': 4, 'name': 'Baked Salmon with Asparagus', 'meal_type': 'dinner', 'dietary_restrictions': 'pescatarian, keto', 'ingredients': 'salmon fillet, asparagus, lemon, garlic, butter', 'instructions': 'Bake salmon and asparagus at 400F for 15 mins.', 'calories': 450, 'protein': 35, 'carbs': 8, 'fat': 28}
            ]

        return jsonify({
            'user_id': user_id,
            'gamma': gamma,
            'lambda_decay': lambda_decay,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        print(f"Error in recommend: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/recommend/meal-plan', methods=['POST'])
def recommend_meal_plan():
    """
    Get personalized meal plan recommendations organized by meal type
    
    Request JSON:
    {
        "user_id": 1,
        "gamma": 0.5,
        "lambda_decay": 2.5,
        "recipes_per_meal": 3
    }
    
    Returns meal plan with breakfast, lunch, snacks, and dinner recommendations
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        gamma = float(data.get('gamma', 0.5))
        lambda_decay = float(data.get('lambda_decay', 2.5))
        recipes_per_meal = int(data.get('recipes_per_meal', 3))
        
        # Validate user_id
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Validate gamma (0-1)
        if not 0 <= gamma <= 1:
            return jsonify({'error': 'gamma must be between 0 and 1'}), 400
        
        # Validate lambda_decay (0.5-4)
        if not 0.5 <= lambda_decay <= 4:
            return jsonify({'error': 'lambda_decay must be between 0.5 and 4'}), 400
        
        # Check if user exists
        user = db.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get meal plan recommendations
        meal_plan = get_meal_plan_recommendations(user_id, gamma, lambda_decay, recipes_per_meal)
        
        # FALLBACK for Cloud Deployments
        if not meal_plan or all(not meals or len(meals) == 0 for meals in meal_plan.values()):
            print("Database returned empty meal plan. Using fallback mock meal plan...")
            meal_plan = {
                "breakfast": [{'id': 2, 'name': 'Oatmeal with Berries', 'meal_type': 'breakfast', 'dietary_restrictions': 'vegetarian', 'ingredients': 'oats, milk, strawberries', 'instructions': 'Boil oats with milk. Top with fresh berries.', 'calories': 250, 'protein': 8, 'carbs': 45, 'fat': 4}],
                "lunch": [{'id': 1, 'name': 'Healthy Grilled Chicken Salad', 'meal_type': 'lunch', 'dietary_restrictions': 'high-protein', 'ingredients': 'chicken breast, lettuce, tomatoes', 'instructions': 'Grill the chicken. Chop vegetables. Toss with olive oil.', 'calories': 350, 'protein': 45, 'carbs': 10, 'fat': 15}],
                "dinner": [{'id': 4, 'name': 'Baked Salmon with Asparagus', 'meal_type': 'dinner', 'dietary_restrictions': 'pescatarian', 'ingredients': 'salmon fillet, asparagus', 'instructions': 'Bake salmon and asparagus at 400F for 15 mins.', 'calories': 450, 'protein': 35, 'carbs': 8, 'fat': 28}],
                "snacks": [{'id': 3, 'name': 'Avocado Toast with Egg', 'meal_type': 'snack', 'dietary_restrictions': 'vegetarian', 'ingredients': 'whole wheat bread, avocado, egg', 'instructions': 'Toast bread. Mash avocado. Top with fried egg.', 'calories': 320, 'protein': 12, 'carbs': 20, 'fat': 22}]
            }

        return jsonify(meal_plan), 200
        
    except Exception as e:
        print(f"Error in meal plan recommend: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== Rating Routes ====================

@app.route('/rate', methods=['POST'])
def rate_recipe():
    """
    Add or update a recipe rating
    
    Request JSON:
    {
        "user_id": 1,
        "recipe_id": 123,
        "rating": 5
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        recipe_id = data.get('recipe_id')
        rating = data.get('rating')
        
        # Validate required fields
        if not all([user_id, recipe_id, rating]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate rating (1-5)
        if not 1 <= rating <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if user and recipe exist
        user = db.get_user_by_id(user_id)
        recipe = db.get_recipe_by_id(recipe_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # Calculate month_index
        timestamp = datetime.now()
        # Get earliest rating timestamp to calculate month_index
        all_ratings = db.get_all_ratings()
        if all_ratings and len(all_ratings) > 0:
            # Convert timestamp string to datetime if needed
            min_timestamp = min(r['timestamp'] for r in all_ratings if r['timestamp'])
            if isinstance(min_timestamp, str):
                min_timestamp = datetime.fromisoformat(min_timestamp.replace('Z', '+00:00'))
            years_diff = timestamp.year - min_timestamp.year
            months_diff = timestamp.month - min_timestamp.month
            month_index = (years_diff * 12) + months_diff + 1
        else:
            month_index = 1
        
        # Add rating
        result = db.add_rating(user_id, recipe_id, rating, timestamp, month_index)
        
        if result:
            return jsonify({
                'message': 'Rating saved successfully',
                'user_id': user_id,
                'recipe_id': recipe_id,
                'rating': rating,
                'timestamp': timestamp.isoformat()
            }), 201
        else:
            return jsonify({'error': 'Failed to save rating'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ratings/<int:user_id>', methods=['GET'])
def get_user_ratings(user_id):
    """
    Get all ratings for a specific user
    """
    try:
        ratings = db.get_user_ratings(user_id)
        return jsonify(ratings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """
    API health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Time-Aware Recipe Recommendation API is running'
    }), 200


# ==================== Diagnostic Route ====================

@app.route('/debug/db', methods=['GET'])
def debug_db():
    """Endpoint to check live database schema on Render"""
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database.sql')
        
        return jsonify({
            "users_table_columns": columns,
            "schema_file_found": os.path.exists(schema_path),
            "db_path": os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'food_db.sqlite'))
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)