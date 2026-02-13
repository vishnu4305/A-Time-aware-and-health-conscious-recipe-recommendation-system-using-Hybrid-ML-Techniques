"""
Health scoring rules for recipe recommendations
Includes BMR calculation, WHO nutritional guidelines, obesity and diabetes extensions
"""
import json


def calculate_bmr(user):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    
    Args:
        user: User dictionary with age, height, weight, gender
    
    Returns:
        BMR in kcal/day
    """
    age = user['age']
    height = user['height']  # cm
    weight = user['weight']  # kg
    gender = user.get('gender', 'male').lower()
    
    # Mifflin-St Jeor Equation
    # BMR = 10*weight(kg) + 6.25*height(cm) - 5*age(y) + s
    # s = +5 for males, -161 for females
    s = 5 if gender == 'male' else -161
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + s
    
    return bmr


def calculate_daily_calories(user):
    """
    Calculate daily calorie needs based on BMR and activity level
    
    Args:
        user: User dictionary with BMR and activity_level
    
    Returns:
        Daily calorie requirement
    """
    bmr = calculate_bmr(user)
    activity_level = user.get('activity_level', 1.2)
    return bmr * activity_level


def check_who_macros(recipe):
    """
    Check if recipe follows WHO nutritional guidelines for macronutrients
    
    WHO Guidelines:
    - Protein: 10-15% of total calories
    - Fat: 15-30% of total calories
    - Carbohydrates: 55-75% of total calories
    
    Args:
        recipe: Recipe dictionary with protein, fat, carbs
    
    Returns:
        Score between 0 and 1 (1 = perfect adherence)
    """
    protein = recipe.get('protein', 0)
    fat = recipe.get('fat', 0)
    carbs = recipe.get('carbs', 0)
    
    # Calculate total macronutrients
    total_macros = protein + fat + carbs
    
    if total_macros == 0:
        return 0
    
    # Calculate percentages
    protein_pct = protein / total_macros
    fat_pct = fat / total_macros
    carbs_pct = carbs / total_macros
    
    score = 0
    
    # Protein: 10-15% (0.10-0.15)
    if 0.10 <= protein_pct <= 0.15:
        score += 0.33
    elif protein_pct < 0.10:
        score += max(0, 0.33 * (protein_pct / 0.10))
    else:  # > 0.15
        score += max(0, 0.33 * (1 - (protein_pct - 0.15) / 0.15))
    
    # Fat: 15-30% (0.15-0.30)
    if 0.15 <= fat_pct <= 0.30:
        score += 0.33
    elif fat_pct < 0.15:
        score += max(0, 0.33 * (fat_pct / 0.15))
    else:  # > 0.30
        score += max(0, 0.33 * (1 - (fat_pct - 0.30) / 0.30))
    
    # Carbs: 55-75% (0.55-0.75)
    if 0.55 <= carbs_pct <= 0.75:
        score += 0.34
    elif carbs_pct < 0.55:
        score += max(0, 0.34 * (carbs_pct / 0.55))
    else:  # > 0.75
        score += max(0, 0.34 * (1 - (carbs_pct - 0.75) / 0.25))
    
    return score


def score_obesity(recipe, user):
    """
    Score recipe for obesity management
    
    Strategy: Calorie deficit of 500 kcal/day
    Penalty if single recipe exceeds 30% of daily calorie allowance
    
    Args:
        recipe: Recipe dictionary with calories
        user: User dictionary with profile
    
    Returns:
        Score adjustment (-0.5 to 0)
    """
    daily_cal = calculate_daily_calories(user)
    deficit_cal = daily_cal - 500  # 500 kcal deficit for weight loss
    
    recipe_cal = recipe.get('calories', 0)
    
    # Penalty if recipe exceeds 30% of daily allowance
    max_meal_cal = deficit_cal * 0.30
    
    if recipe_cal > max_meal_cal:
        # Progressive penalty based on how much it exceeds
        excess_ratio = (recipe_cal - max_meal_cal) / max_meal_cal
        penalty = min(0.5, excess_ratio * 0.5)
        return -penalty
    
    return 0


def score_diabetes(recipe, user):
    """
    Score recipe for diabetes management
    
    Strategy: Limit sugar and glycemic load
    - Penalty if sugar > 10g
    - Penalty if Glycemic Load (GL) > 15
    
    Args:
        recipe: Recipe dictionary with sugar and gl
        user: User dictionary with profile
    
    Returns:
        Score adjustment (-0.5 to 0)
    """
    sugar = recipe.get('sugar', 0)
    gl = recipe.get('gl', 0)
    
    penalty = 0
    
    # Sugar penalty (>10g is high)
    if sugar > 10:
        excess_sugar = sugar - 10
        penalty += min(0.3, (excess_sugar / 20) * 0.3)  # Max 0.3 penalty
    
    # Glycemic Load penalty (>15 is high)
    if gl > 15:
        excess_gl = gl - 15
        penalty += min(0.2, (excess_gl / 10) * 0.2)  # Max 0.2 penalty
    
    return -penalty


def calculate_health_score(recipe, user):
    """
    Calculate comprehensive health score for a recipe based on user profile
    
    Args:
        recipe: Recipe dictionary with nutritional information
        user: User dictionary with profile and conditions
    
    Returns:
        Health score between 0 and 1
    """
    # Base score from WHO macro guidelines
    score = check_who_macros(recipe)
    
    # Parse conditions
    conditions = user.get('conditions', [])
    if isinstance(conditions, str):
        try:
            conditions = json.loads(conditions)
        except:
            conditions = []
    
    # Apply condition-specific scoring
    if 'obesity' in conditions:
        score += score_obesity(recipe, user)
    
    if 'diabetes' in conditions:
        score += score_diabetes(recipe, user)
    
    # Ensure score is between 0 and 1
    return max(0, min(1, score))


def get_health_explanation(recipe, user):
    """
    Generate explanation for health score
    
    Args:
        recipe: Recipe dictionary
        user: User dictionary
    
    Returns:
        String explanation
    """
    explanations = []
    
    # WHO macros
    who_score = check_who_macros(recipe)
    if who_score >= 0.8:
        explanations.append("Excellent macro balance")
    elif who_score >= 0.5:
        explanations.append("Good macro balance")
    else:
        explanations.append("Could improve macro balance")
    
    # Conditions
    conditions = user.get('conditions', [])
    if isinstance(conditions, str):
        try:
            conditions = json.loads(conditions)
        except:
            conditions = []
    
    if 'obesity' in conditions:
        obesity_score = score_obesity(recipe, user)
        if obesity_score == 0:
            explanations.append("Calorie-appropriate for weight loss")
        else:
            explanations.append("High calorie for weight loss goal")
    
    if 'diabetes' in conditions:
        diabetes_score = score_diabetes(recipe, user)
        if diabetes_score == 0:
            explanations.append("Diabetes-friendly (low sugar/GL)")
        else:
            sugar = recipe.get('sugar', 0)
            gl = recipe.get('gl', 0)
            if sugar > 10:
                explanations.append(f"High sugar ({sugar}g)")
            if gl > 15:
                explanations.append(f"High glycemic load ({gl})")
    
    return " | ".join(explanations) if explanations else "Standard nutritional profile"
