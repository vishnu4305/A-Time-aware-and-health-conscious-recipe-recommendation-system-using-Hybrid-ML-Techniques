"""

Time-Aware Health-Conscious Recipe Recommendation System
Flask Backend API

"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import threading
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

# Load ML data in the background to prevent Render deployment timeouts
def background_load():
    print("Background thread: Loading recipe and ML data...")
    try:
        load_data()
        print("Background thread: ML Data loaded successfully!")
    except Exception as e:
        print(f"Background thread error: {e}")

# Disable background loading to prevent Out-Of-Memory (OOM) crashes on Render's Free Tier.
# Data will be "lazy-loaded" on the very first recommendation request instead.
# threading.Thread(target=background_load, daemon=True).start()


# ==================== Root Route ====================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'Welcome to the Time-Aware Recipe Recommendation API!'
    }), 200

# ==================== User Routes ====================

@app.route('/user/login', methods=['POST'])
def login_user():
    """
    Login an existing user
    
    Request JSON:
    {
        "username": "vishnu123"
    }
    """
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
            
        user = db.get_user_by_username(username)
        if user:
            user_id = user.get('_id') or user.get('id')
            return jsonify({
                'message': 'Login successful',
                'user_id': str(user_id),
                'user': user
            }), 200
        else:
            return jsonify({'error': 'User not found. Please register.'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
            return jsonify({'error': 'Username already exists. Please choose another one or login.'}), 409
        
        # Create new user
        user_id = db.create_user(username, name, age, height, weight, gender, conditions, activity_level)
        
        if user_id:
            user = db.get_user_by_id(user_id)
            return jsonify({
                'message': 'User created successfully',
                # Convert ObjectId to string for JSON serialization
                'user_id': str(user_id),
                'user': user
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        app.logger.error(f"An error occurred while creating a user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': "An internal server error occurred."}), 500


@app.route('/user/<string:user_id>', methods=['GET'])
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


@app.route('/user/update/<string:user_id>', methods=['PUT'])
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
        limit = request.args.get('limit', default=50, type=int)
        recipes = db.get_all_recipes(limit=limit)
        
        return jsonify(recipes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/recipes/<string:recipe_id>', methods=['GET'])
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
        
        # COLD START FALLBACK: If ML model returns empty (for new users), pull real recipes from the downloaded DB
        if not recommendations or len(recommendations) == 0:
            print("ML Model returned 0 recipes (Cold Start). Pulling real recipes from DB directly...")
            projection = {
                '_id': 1, 'name': 1, 'ingredients': 1, 'minutes': 1, 'n_ingredients': 1, 
                'calories': 1, 'total_fat': 1, 'sugar': 1, 'sodium': 1, 'protein': 1, 
                'saturated_fat': 1, 'carbohydrates': 1
            }
            fallback_recs = db.get_random_recipes(top_n, projection=projection)
            if fallback_recs:
                recommendations = fallback_recs

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
        
        # COLD START FALLBACK FOR MEAL PLAN:
        if not meal_plan or all(not meals or len(meals) == 0 for meals in meal_plan.values()):
            print("ML Model returned empty meal plan. Pulling real recipes from DB directly...")
            projection = {
                '_id': 1, 'name': 1, 'ingredients': 1, 'minutes': 1, 'n_ingredients': 1, 
                'calories': 1, 'total_fat': 1, 'sugar': 1, 'sodium': 1, 'protein': 1, 
                'saturated_fat': 1, 'carbohydrates': 1
            }
            meal_plan = {
                "breakfast": db.get_recipes_with_offset(0, recipes_per_meal, projection) or [],
                "lunch": db.get_recipes_with_offset(10, recipes_per_meal, projection) or [],
                "dinner": db.get_recipes_with_offset(20, recipes_per_meal, projection) or [],
                "snacks": db.get_recipes_with_offset(30, recipes_per_meal, projection) or []
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
        min_timestamp_str = db.get_earliest_rating_timestamp()
        if min_timestamp_str:
            min_dt = datetime.fromisoformat(min_timestamp_str.replace('Z', '+00:00'))
            years_diff = timestamp.year - min_dt.year
            months_diff = timestamp.month - min_dt.month
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


@app.route('/ratings/<string:user_id>', methods=['GET'])
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
    """Endpoint to check live database connection to MongoDB"""
    try:
        database = db.get_db()
        recipe_count = database.recipes.count_documents({})
        rating_count = database.ratings.count_documents({})
        
        return jsonify({
            "status": "connected",
            "recipe_count": recipe_count,
            "rating_count": rating_count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)