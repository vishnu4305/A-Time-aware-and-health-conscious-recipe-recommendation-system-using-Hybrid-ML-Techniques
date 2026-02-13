"""
Main recommendation engine combining time-aware collaborative filtering,
content-based filtering, and health-conscious scoring
"""
import sys
import os
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Add backend to path for database access
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
import database as db

from .embeddings import get_or_compute_embeddings, encode_user_profile, compute_similarity
from .health_rules import calculate_health_score, get_health_explanation


# Global cache for data
_recipes_df = None
_ratings_df = None
_embeddings = None
_max_month_index = None
_cached_rating_count = 0  # Track rating count for smart caching


def load_data():
    """
    Load recipes and ratings data from database into memory
    Cache for performance
    """
    global _recipes_df, _ratings_df, _embeddings, _max_month_index, _cached_rating_count
    
    # Load recipes
    recipes = db.get_all_recipes()
    _recipes_df = pd.DataFrame(recipes)
    
    # Load ratings
    ratings = db.get_all_ratings()
    _ratings_df = pd.DataFrame(ratings) if ratings else pd.DataFrame()
    
    # Filter out ratings for recipes that don't exist
    if not _ratings_df.empty and not _recipes_df.empty:
        valid_recipe_ids = set(_recipes_df['id'].tolist())
        original_count = len(_ratings_df)
        _ratings_df = _ratings_df[_ratings_df['recipe_id'].isin(valid_recipe_ids)]
        filtered_count = original_count - len(_ratings_df)
        if filtered_count > 0:
            print(f"Filtered out {filtered_count} ratings for non-existent recipes")
    
    # Calculate max month_index (TP - Total Periods)
    if not _ratings_df.empty and 'month_index' in _ratings_df.columns:
        _max_month_index = _ratings_df['month_index'].max()
    else:
        _max_month_index = 1
    
    # Initialize cached rating count
    _cached_rating_count = len(_ratings_df)
    
    # Load or compute embeddings
    embeddings_path = os.path.join(os.path.dirname(__file__), 'embeddings', 'recipe_embeddings.npy')
    
    if not _recipes_df.empty:
        ingredients_list = _recipes_df['ingredients'].tolist()
        _embeddings = get_or_compute_embeddings(ingredients_list, embeddings_path)
    
    print(f"Data loaded: {len(_recipes_df)} recipes, {len(_ratings_df)} ratings")


def reload_ratings():
    """
    Reload ONLY ratings data from database to capture new user ratings
    Uses smart caching: only reloads if rating count has changed
    This dramatically improves performance (20-30x faster)
    """
    global _ratings_df, _max_month_index, _cached_rating_count
    
    # Quick check: Get current rating count from database
    current_count = db.get_rating_count()
    
    # If count hasn't changed, skip expensive reload
    if current_count == _cached_rating_count and _ratings_df is not None:
        print(f"Ratings cache hit: {_cached_rating_count} ratings (no reload needed)")
        return
    
    # Count changed - reload ratings from database
    print(f"Ratings cache miss: {_cached_rating_count} -> {current_count} (reloading...)")
    ratings = db.get_all_ratings()
    _ratings_df = pd.DataFrame(ratings) if ratings else pd.DataFrame()
    
    # Filter out ratings for recipes that don't exist
    if not _ratings_df.empty and _recipes_df is not None and not _recipes_df.empty:
        valid_recipe_ids = set(_recipes_df['id'].tolist())
        _ratings_df = _ratings_df[_ratings_df['recipe_id'].isin(valid_recipe_ids)]
    
    # Recalculate max month_index
    if not _ratings_df.empty and 'month_index' in _ratings_df.columns:
        _max_month_index = _ratings_df['month_index'].max()
    else:
        _max_month_index = 1
    
    # Update cached count
    _cached_rating_count = len(_ratings_df)
    print(f"Ratings reloaded: {_cached_rating_count} total ratings")


def time_aware_collaborative_filtering(user_id, lambda_decay=2.5):
    """
    Time-Aware Collaborative Filtering based on Rostami et al. (2023)
    
    Computes user similarity with time weights applied to common ratings
    TW = exp(-λ * (TP - t_ui)) + exp(-λ * (TP - t_uj))
    
    Args:
        user_id: Target user ID
        lambda_decay: Time decay parameter (default 2.5)
    
    Returns:
        Predicted scores for all recipes
    """
    if _ratings_df.empty:
        return np.zeros(len(_recipes_df))
    
    # Get user's ratings
    user_ratings = _ratings_df[_ratings_df['user_id'] == user_id]
    if user_ratings.empty:
        return np.zeros(len(_recipes_df))
    
    # Pre-index ratings for fast lookup: (user_id, recipe_id) -> (rating, month_index)
    # Using vectorized operations instead of iterrows() for 100x speedup
    rating_lookup = {
        (int(uid), int(rid)): (float(rating), int(month))
        for uid, rid, rating, month in zip(
            _ratings_df['user_id'],
            _ratings_df['recipe_id'],
            _ratings_df['rating'],
            _ratings_df['month_index']
        )
    }
    
    # Get users who rated similar items
    user_items = {int(r['recipe_id']): float(r['rating']) for _, r in user_ratings.iterrows()}
    user_mean = user_ratings['rating'].mean()
    
    # Find other users who rated at least one common item
    common_recipe_ids = set(user_items.keys())
    potential_users = _ratings_df[_ratings_df['recipe_id'].isin(common_recipe_ids)]['user_id'].unique()
    potential_users = [int(u) for u in potential_users if int(u) != user_id]
    
    # Calculate mean ratings per user (only for relevant users)
    mean_ratings = _ratings_df.groupby('user_id')['rating'].mean().to_dict()
    
    # Compute time-aware similarities
    user_similarities = []
    
    # Reduced from 500 to 50 for 10x speedup (still finds good neighbors)
    for other_user in potential_users[:50]:
        # Get other user's ratings using pre-indexed lookup
        other_items = {}
        for recipe_id in common_recipe_ids:
            key = (other_user, recipe_id)
            if key in rating_lookup:
                other_items[recipe_id] = rating_lookup[key][0]
        
        # Find common items
        common_items = set(user_items.keys()) & set(other_items.keys())
        
        if len(common_items) < 2:  # Need at least 2 common items
            continue
        
        # Calculate time-weighted similarity
        numerator = 0
        denom_user_sq = 0
        denom_other_sq = 0
        
        for item in common_items:
            # Get timestamps using pre-indexed lookup
            user_key = (user_id, item)
            other_key = (other_user, item)
            
            if user_key not in rating_lookup or other_key not in rating_lookup:
                continue
            
            t_ui = rating_lookup[user_key][1]
            t_uj = rating_lookup[other_key][1]
            
            # Time Weight (TW) - Equation 2 from Rostami paper
            tw = np.exp(-lambda_decay * (_max_month_index - t_ui)) + \
                 np.exp(-lambda_decay * (_max_month_index - t_uj))
            
            # Deviation from mean
            dev_ui = user_items[item] - mean_ratings[user_id]
            dev_uj = other_items[item] - mean_ratings[other_user]
            
            # Accumulate
            numerator += dev_ui * dev_uj * tw
            denom_user_sq += (dev_ui ** 2) * tw
            denom_other_sq += (dev_uj ** 2) * tw
        
        # Calculate similarity
        if denom_user_sq > 0 and denom_other_sq > 0:
            similarity = numerator / (np.sqrt(denom_user_sq) * np.sqrt(denom_other_sq))
            user_similarities.append((other_user, similarity))
            
            # Early stopping: if we have 20 users with good similarity, we're done
            if len(user_similarities) >= 20 and min(s[1] for s in user_similarities) > 0.5:
                break
    
    if not user_similarities:
        return np.zeros(len(_recipes_df))
    
    # Sort by similarity and take top 20
    user_similarities.sort(key=lambda x: x[1], reverse=True)
    top_similar_users = user_similarities[:20]
    
    # Predict ratings for all recipes
    predicted_scores = np.zeros(len(_recipes_df))
    
    # Pre-compute ratings by similar users for faster lookup
    similar_user_ratings = {}
    for other_user, _ in top_similar_users:
        for recipe_id in range(len(_recipes_df)):
            actual_recipe_id = int(_recipes_df.iloc[recipe_id]['id'])
            key = (other_user, actual_recipe_id)
            if key in rating_lookup:
                if actual_recipe_id not in similar_user_ratings:
                    similar_user_ratings[actual_recipe_id] = []
                similar_user_ratings[actual_recipe_id].append((
                    other_user,
                    rating_lookup[key][0]
                ))
    
    # Get all recipes
    for idx, recipe_id in enumerate(_recipes_df['id']):
        recipe_id = int(recipe_id)
        
        # Weighted average of similar users' ratings
        if recipe_id not in similar_user_ratings:
            continue
            
        numerator = 0
        denominator = 0
        
        for other_user, other_rating in similar_user_ratings[recipe_id]:
            # Find similarity for this user
            similarity = next((sim for u, sim in top_similar_users if u == other_user), 0)
            if similarity > 0:
                numerator += similarity * (other_rating - mean_ratings[other_user])
                denominator += abs(similarity)
        
        if denominator > 0:
            predicted_scores[idx] = user_mean + (numerator / denominator)
    
    # Normalize to 0-1
    if predicted_scores.max() > 0:
        predicted_scores = predicted_scores / predicted_scores.max()
    
    return predicted_scores


def content_based_filtering(user_id):
    """
    Content-Based Filtering using ingredient embeddings
    
    Creates user profile from rated recipes and computes similarity
    
    Args:
        user_id: Target user ID
    
    Returns:
        Content similarity scores for all recipes
    """
    if _ratings_df.empty or _embeddings is None:
        return np.zeros(len(_recipes_df))
    
    # Get user's rated recipes
    user_ratings = _ratings_df[_ratings_df['user_id'] == user_id]
    
    if user_ratings.empty:
        return np.zeros(len(_recipes_df))
    
    # Get ingredients from rated recipes
    rated_recipe_ids = user_ratings['recipe_id'].tolist()
    rated_ingredients = _recipes_df[_recipes_df['id'].isin(rated_recipe_ids)]['ingredients'].tolist()
    
    # Create user profile embedding
    user_embedding = encode_user_profile(rated_ingredients)
    
    if user_embedding is None:
        return np.zeros(len(_recipes_df))
    
    # Compute similarity with all recipes
    similarities = compute_similarity(user_embedding, _embeddings)[0]
    
    # Normalize
    if similarities.max() > 0:
        similarities = similarities / similarities.max()
    
    return similarities


def health_based_scoring(user_id):
    """
    Health-Based Scoring using nutritional guidelines and user conditions
    
    Args:
        user_id: Target user ID
    
    Returns:
        Health scores for all recipes
    """
    user = db.get_user_by_id(user_id)
    
    if not user:
        return np.zeros(len(_recipes_df))
    
    health_scores = []
    
    for _, recipe in _recipes_df.iterrows():
        score = calculate_health_score(recipe.to_dict(), user)
        health_scores.append(score)
    
    return np.array(health_scores)


def get_recommendations(user_id, gamma=0.5, lambda_decay=2.5, top_n=10):
    """
    Get personalized recipe recommendations
    
    Combines time-aware CF, content-based, and health scoring using gamma parameter
    
    Args:
        user_id: Target user ID
        gamma: Balance between taste and health (0=pure taste, 1=pure health)
        lambda_decay: Time decay parameter for CF
        top_n: Number of recommendations to return
    
    Returns:
        List of recommended recipes with explanations
    """
    # Load data if not already loaded
    if _recipes_df is None or _ratings_df is None:
        load_data()
    else:
        # Reload ratings to capture any new user ratings
        reload_ratings()
    
    if _recipes_df.empty:
        return []
    
    # Get user profile
    user = db.get_user_by_id(user_id)
    if not user:
        return []
    
    # 1. Time-Aware Collaborative Filtering
    cf_scores = time_aware_collaborative_filtering(user_id, lambda_decay)
    
    # 2. Content-Based Filtering
    content_scores = content_based_filtering(user_id)
    
    # 3. Health Scoring
    health_scores = health_based_scoring(user_id)
    
    # 4. Fuse scores with gamma
    # Preference = 0.6 * CF + 0.4 * Content
    preference_scores = 0.6 * cf_scores + 0.4 * content_scores
    
    # Normalize preference scores
    if preference_scores.max() > 0:
        preference_scores = preference_scores / preference_scores.max()
    
    # Final score = (1-γ) * preference + γ * health
    final_scores = (1 - gamma) * preference_scores + gamma * health_scores
    
    # Get user's ratings to preserve top-rated favorites
    user_ratings = _ratings_df[_ratings_df['user_id'] == user_id]
    
    # Build recipe_id to index mapping
    recipe_id_to_idx = {int(recipe_id): idx for idx, recipe_id in enumerate(_recipes_df['id'])}
    
    recommendations = []
    
    # STEP 1: Get top 3 highest-rated recipes (user's favorites)
    if not user_ratings.empty:
        # Sort user ratings by rating score (descending)
        top_rated = user_ratings.nlargest(3, 'rating')
        
        for _, rating_row in top_rated.iterrows():
            recipe_id = int(rating_row['recipe_id'])
            if recipe_id in recipe_id_to_idx:
                idx = recipe_id_to_idx[recipe_id]
                recipe = _recipes_df.iloc[idx].to_dict()
                
                # Add scores and explanation
                recipe['final_score'] = float(final_scores[idx])
                recipe['preference_score'] = float(preference_scores[idx])
                recipe['health_score'] = float(health_scores[idx])
                recipe['gamma_used'] = gamma
                recipe['lambda_used'] = lambda_decay
                recipe['user_rating'] = float(rating_row['rating'])  # Mark as user's favorite
                
                # Generate explanation
                explanation_parts = []
                explanation_parts.append(f"⭐ Your Rating: {rating_row['rating']:.0f}/5")
                explanation_parts.append(f"Taste: {preference_scores[idx]:.2f}")
                explanation_parts.append(f"Health: {health_scores[idx]:.2f}")
                
                health_explanation = get_health_explanation(recipe, user)
                if health_explanation:
                    explanation_parts.append(health_explanation)
                
                recipe['explanation'] = " | ".join(explanation_parts)
                recommendations.append(recipe)
    
    # STEP 2: Fill remaining slots with best unrated recipes
    rated_recipe_ids = set(user_ratings['recipe_id'].tolist()) if not user_ratings.empty else set()
    remaining_slots = top_n - len(recommendations)
    
    if remaining_slots > 0:
        # Create scores array excluding already-rated recipes
        unrated_scores = final_scores.copy()
        for idx, recipe_id in enumerate(_recipes_df['id']):
            if int(recipe_id) in rated_recipe_ids:
                unrated_scores[idx] = -1  # Mask out rated recipes
        
        # Get top unrated recipes
        top_unrated_indices = np.argsort(unrated_scores)[::-1][:remaining_slots]
        
        for idx in top_unrated_indices:
            if unrated_scores[idx] < 0:  # Skip masked recipes
                continue
                
            recipe = _recipes_df.iloc[idx].to_dict()
            
            # Add scores and explanation
            recipe['final_score'] = float(final_scores[idx])
            recipe['preference_score'] = float(preference_scores[idx])
            recipe['health_score'] = float(health_scores[idx])
            recipe['gamma_used'] = gamma
            recipe['lambda_used'] = lambda_decay
            
            # Generate explanation
            explanation_parts = []
            explanation_parts.append(f"Taste: {preference_scores[idx]:.2f}")
            explanation_parts.append(f"Health: {health_scores[idx]:.2f}")
            explanation_parts.append(f"Final: {final_scores[idx]:.2f}")
            
            health_explanation = get_health_explanation(recipe, user)
            if health_explanation:
                explanation_parts.append(health_explanation)
            
            recipe['explanation'] = " | ".join(explanation_parts)
            recommendations.append(recipe)
    
    return recommendations


def get_meal_plan_recommendations(user_id, gamma=0.5, lambda_decay=2.5, recipes_per_meal=3):
    """
    Get meal plan recommendations organized by meal type (breakfast, lunch, snacks, dinner)
    
    Uses existing recommendation engine and adds meal classification on top
    
    Args:
        user_id: Target user ID
        gamma: Balance between taste and health (0=pure taste, 1=pure health)
        lambda_decay: Time decay parameter for CF
        recipes_per_meal: Number of recipes to recommend per meal type
    
    Returns:
        Dictionary with meal plan organized by meal type
    """
    from .meal_classifier import classify_recipes_batch
    from .meal_planner import create_meal_plan
    
    # Load data if not already loaded
    if _recipes_df is None or _ratings_df is None:
        load_data()
    else:
        # Reload ratings to capture any new user ratings
        reload_ratings()
    
    if _recipes_df.empty:
        return {
            'meal_plan': {
                'breakfast': {'target_calories': 0, 'recipes': [], 'count': 0},
                'lunch': {'target_calories': 0, 'recipes': [], 'count': 0},
                'snacks': {'target_calories': 0, 'recipes': [], 'count': 0},
                'dinner': {'target_calories': 0, 'recipes': [], 'count': 0}
            },
            'daily_calories': 0,
            'calorie_distribution': {}
        }
    
    # Get user profile
    user = db.get_user_by_id(user_id)
    if not user:
        return {
            'meal_plan': {
                'breakfast': {'target_calories': 0, 'recipes': [], 'count': 0},
                'lunch': {'target_calories': 0, 'recipes': [], 'count': 0},
                'snacks': {'target_calories': 0, 'recipes': [], 'count': 0},
                'dinner': {'target_calories': 0, 'recipes': [], 'count': 0}
            },
            'daily_calories': 0,
            'calorie_distribution': {}
        }
    
    # Get top 50 recommendations using existing algorithm
    # More recipes = better chance of finding suitable ones for each meal type
    all_recommendations = get_recommendations(user_id, gamma, lambda_decay, top_n=50)
    
    if not all_recommendations:
        return {
            'meal_plan': {
                'breakfast': {'target_calories': 0, 'recipes': [], 'count': 0},
                'lunch': {'target_calories': 0, 'recipes': [], 'count': 0},
                'snacks': {'target_calories': 0, 'recipes': [], 'count': 0},
                'dinner': {'target_calories': 0, 'recipes': [], 'count': 0}
            },
            'daily_calories': 0,
            'calorie_distribution': {}
        }
    
    # Classify recipes by meal type
    classified_recipes = classify_recipes_batch(all_recommendations)
    
    # Create meal plan with calorie distribution
    meal_plan_result = create_meal_plan(classified_recipes, user, recipes_per_meal)
    
    # Add metadata
    meal_plan_result['gamma_used'] = gamma
    meal_plan_result['lambda_used'] = lambda_decay
    meal_plan_result['user_id'] = user_id
    
    return meal_plan_result


# Initialize data on module import
try:
    load_data()
except Exception as e:
    print(f"Warning: Could not load initial data: {e}")
    print("Data will be loaded on first recommendation request")
