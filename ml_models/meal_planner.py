"""
Meal Planner
Calculates daily calorie distribution and selects appropriate recipes for each meal
"""
import json
import os
from typing import Dict, List
from .health_rules import calculate_bmr


def load_meal_distribution() -> Dict[str, float]:
    """Load meal calorie distribution percentages from config"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'meal_distribution.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def get_activity_multiplier(activity_level: str) -> float:
    """
    Get TDEE multiplier based on activity level
    
    Args:
        activity_level: sedentary, lightly_active, moderately_active, very_active, extra_active
    
    Returns:
        Float multiplier for BMR
    """
    multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extra_active': 1.9
    }
    return multipliers.get(activity_level, 1.55)  # Default to moderately active


def calculate_tdee(user: Dict) -> float:
    """
    Calculate Total Daily Energy Expenditure
    
    Args:
        user: User dictionary with age, height, weight, gender, activity_level
    
    Returns:
        TDEE in calories
    """
    bmr = calculate_bmr(user)
    activity_level = user.get('activity_level', 'moderately_active')
    multiplier = get_activity_multiplier(activity_level)
    
    return bmr * multiplier


def calculate_daily_distribution(user: Dict) -> Dict[str, float]:
    """
    Calculate calorie targets for each meal type
    
    Args:
        user: User dictionary
    
    Returns:
        Dictionary mapping meal types to calorie targets
    """
    tdee = calculate_tdee(user)
    distribution = load_meal_distribution()
    
    # Adjust for conditions
    conditions = user.get('conditions', [])
    if isinstance(conditions, str):
        try:
            conditions = json.loads(conditions)
        except:
            conditions = []
    
    # If obesity, reduce total by 500 calories for deficit
    if 'obesity' in conditions:
        tdee -= 500
    
    return {
        meal_type: tdee * percentage
        for meal_type, percentage in distribution.items()
    }


def select_recipes_for_meal(
    candidates: List[Dict],
    target_calories: float,
    count: int = 3,
    tolerance: float = 0.5
) -> List[Dict]:
    """
    Select best recipes for a specific meal based on calorie fit and score
    
    Args:
        candidates: List of candidate recipes for this meal type
        target_calories: Target calorie amount for this meal
        count: Number of recipes to return
        tolerance: Acceptable calorie deviation (0.5 = 50%)
    
    Returns:
        List of selected recipes with calorie_fitness score added
    """
    if not candidates:
        return []
    
    # Calculate calorie fitness for each candidate
    suitable = []
    for recipe in candidates:
        recipe_calories = float(recipe.get('calories', 0))
        if recipe_calories == 0:
            continue
        
        # Calculate how well it fits the calorie target
        deviation = abs(recipe_calories - target_calories) / target_calories
        
        if deviation <= tolerance:
            calorie_fitness = 1 - deviation
            recipe['calorie_fitness'] = calorie_fitness
            recipe['target_calories'] = target_calories
            suitable.append(recipe)
    
    # If not enough suitable recipes, include some from outside tolerance
    if len(suitable) < count and len(candidates) > len(suitable):
        for recipe in candidates:
            if recipe not in suitable:
                recipe_calories = float(recipe.get('calories', 0))
                if recipe_calories > 0:
                    deviation = abs(recipe_calories - target_calories) / target_calories
                    calorie_fitness = max(0, 1 - deviation)
                    recipe['calorie_fitness'] = calorie_fitness
                    recipe['target_calories'] = target_calories
                    suitable.append(recipe)
    
    # Sort by calorie fitness first, then by recommendation score
    suitable.sort(
        key=lambda x: (x.get('calorie_fitness', 0), x.get('final_score', 0)),
        reverse=True
    )
    
    # Ensure variety - no duplicate main ingredients
    selected = []
    used_ingredients = set()
    
    for recipe in suitable:
        if len(selected) >= count:
            break
        
        # Extract main ingredient (first word of recipe name)
        main_ingredient = str(recipe.get('name', '')).split()[0].lower()
        
        if main_ingredient not in used_ingredients:
            selected.append(recipe)
            used_ingredients.add(main_ingredient)
    
    # If still not enough, add more without ingredient check
    if len(selected) < count:
        for recipe in suitable:
            if recipe not in selected:
                selected.append(recipe)
                if len(selected) >= count:
                    break
    
    return selected[:count]


def create_meal_plan(
    classified_recipes: Dict[str, List[Dict]],
    user: Dict,
    recipes_per_meal: int = 3
) -> Dict:
    """
    Create a complete daily meal plan
    
    Args:
        classified_recipes: Dictionary of recipes grouped by meal type
        user: User dictionary
        recipes_per_meal: Number of recipes to suggest per meal
    
    Returns:
        Dictionary with meal plan and calorie information
    """
    meal_budgets = calculate_daily_distribution(user)
    tdee = calculate_tdee(user)
    
    meal_plan = {}
    
    for meal_type in ['breakfast', 'lunch', 'snacks', 'dinner']:
        target_calories = meal_budgets[meal_type]
        candidates = classified_recipes.get(meal_type, [])
        
        # Try with normal tolerance first
        selected = select_recipes_for_meal(
            candidates,
            target_calories,
            recipes_per_meal,
            tolerance=0.5
        )
        
        # If no recipes found, try 'any_meal' category
        if not selected or len(selected) < recipes_per_meal:
            candidates = classified_recipes.get('any_meal', [])
            selected = select_recipes_for_meal(
                candidates,
                target_calories,
                recipes_per_meal,
                tolerance=0.5
            )
        
        # If still no recipes, relax tolerance to 100% (double or half target calories)
        if not selected or len(selected) < recipes_per_meal:
            all_candidates = classified_recipes.get(meal_type, []) + classified_recipes.get('any_meal', [])
            selected = select_recipes_for_meal(
                all_candidates,
                target_calories,
                recipes_per_meal,
                tolerance=1.0
            )
        
        meal_plan[meal_type] = {
            'target_calories': round(target_calories, 1),
            'recipes': selected,
            'count': len(selected)
        }
    
    return {
        'meal_plan': meal_plan,
        'daily_calories': round(tdee, 1),
        'calorie_distribution': {k: round(v, 1) for k, v in meal_budgets.items()}
    }
