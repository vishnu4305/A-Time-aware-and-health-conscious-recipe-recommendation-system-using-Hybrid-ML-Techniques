"""
Meal Type Classifier
Classifies recipes into meal categories (breakfast, lunch, snacks, dinner)
using a scoring system based on keywords, ingredients, and nutritional profiles
"""
import json
import os
from typing import Dict, List, Tuple


def load_meal_config() -> Dict:
    """Load meal classification configuration from JSON"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'meal_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def classify_recipe(recipe: Dict) -> str:
    """
    Classify a recipe into a meal type using scoring system
    
    Scoring:
    - Name keyword match: +5 points each (prioritizes what it IS)
    - Ingredient match: +2 points each
    - Calorie range fit: +2 points (de-emphasized)
    - Macro profile fit: +2 points per criterion
    
    This scoring focuses on recipe type (keywords/ingredients)
    rather than calorie count, allowing healthy low-cal recipes
    to still be classified as dinner if they match dinner keywords.
    
    Args:
        recipe: Dictionary with keys: name, ingredients, calories, protein, fat, carbs
    
    Returns:
        Meal type string: 'breakfast', 'lunch', 'snacks', 'dinner', or 'any_meal'
    """
    config = load_meal_config()
    scores = {}
    
    recipe_name = str(recipe.get('name', '')).lower()
    recipe_ingredients = str(recipe.get('ingredients', '')).lower()
    recipe_calories = float(recipe.get('calories', 0))
    
    # Get macros (as percentage of total calories)
    total_cals = recipe_calories
    if total_cals > 0:
        protein_pct = (float(recipe.get('protein', 0)) * 4 / total_cals) * 100
        carbs_pct = (float(recipe.get('carbohydrates', 0)) * 4 / total_cals) * 100
        fat_pct = (float(recipe.get('total_fat', 0)) * 9 / total_cals) * 100
    else:
        protein_pct = carbs_pct = fat_pct = 0
    
    for meal_type, criteria in config.items():
        score = 0
        
        # 1. Name keyword matching (+5 each) - INCREASED from +3
        for keyword in criteria['keywords']:
            if keyword.lower() in recipe_name:
                score += 5
        
        # 2. Ingredient matching (+2 each) - INCREASED from +1
        for ingredient in criteria['ingredients']:
            if ingredient.lower() in recipe_ingredients:
                score += 2
        
        # 3. Calorie range fit (+2) - REDUCED from +5
        cal_min, cal_max = criteria['calorie_range']
        if cal_min <= recipe_calories <= cal_max:
            score += 2
        elif recipe_calories > 0:
            # Partial score if close to range
            distance = min(abs(recipe_calories - cal_min), abs(recipe_calories - cal_max))
            if distance < 200:  # Within 200 calories
                score += 1  # REDUCED from +2
        
        # 4. Macro profile fit (+2 each)
        macro_profile = criteria.get('macro_profile', {})
        
        if 'carbs_min' in macro_profile and carbs_pct >= macro_profile['carbs_min']:
            score += 2
        if 'carbs_max' in macro_profile and carbs_pct <= macro_profile['carbs_max']:
            score += 2
        if 'protein_min' in macro_profile and protein_pct >= macro_profile['protein_min']:
            score += 2
        if 'protein_max' in macro_profile and protein_pct <= macro_profile['protein_max']:
            score += 2
        if 'calories_max' in macro_profile and recipe_calories <= macro_profile['calories_max']:
            score += 2
        
        scores[meal_type] = score
    
    # Find meal type with highest score
    if not scores or max(scores.values()) == 0:
        return 'any_meal'  # No clear classification
    
    max_score = max(scores.values())
    best_meals = [meal for meal, score in scores.items() if score == max_score]
    
    # If tie, use priority order
    priority = ['breakfast', 'lunch', 'dinner', 'snacks']
    for meal in priority:
        if meal in best_meals:
            return meal
    
    return best_meals[0]


def classify_recipes_batch(recipes: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classify multiple recipes and group by meal type
    
    Args:
        recipes: List of recipe dictionaries
    
    Returns:
        Dictionary mapping meal types to lists of recipes
    """
    classified = {
        'breakfast': [],
        'lunch': [],
        'snacks': [],
        'dinner': [],
        'any_meal': []
    }
    
    for recipe in recipes:
        meal_type = classify_recipe(recipe)
        recipe['meal_type'] = meal_type
        classified[meal_type].append(recipe)
    
    return classified


def get_meal_type_summary(recipes: List[Dict]) -> Dict[str, int]:
    """
    Get count of recipes by meal type
    
    Args:
        recipes: List of recipe dictionaries
    
    Returns:
        Dictionary with counts per meal type
    """
    summary = {'breakfast': 0, 'lunch': 0, 'snacks': 0, 'dinner': 0, 'any_meal': 0}
    
    for recipe in recipes:
        meal_type = classify_recipe(recipe)
        summary[meal_type] += 1
    
    return summary
