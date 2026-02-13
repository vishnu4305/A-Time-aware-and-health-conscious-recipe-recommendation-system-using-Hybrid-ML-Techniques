"""
Data Preprocessing Script
Processes raw Food.com dataset to add:
1. Glycemic Load (GL) calculation
2. Month index for time-aware recommendations
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os


def preprocess_recipes(input_file='RAW_recipes.csv', output_file='recipes_processed.csv'):
    """
    Preprocess recipes data
    
    - Add Glycemic Load (GL) estimation
    - Clean nutritional data
    """
    print(f"Loading recipes from {input_file}...")
    
    # Read recipes
    recipes = pd.read_csv(input_file)
    
    print(f"Loaded {len(recipes)} recipes")
    
    # Extract nutrition information (stored as list in string format)
    # Nutrition format: [calories, total fat, sugar, sodium, protein, saturated fat, carbohydrates]
    if 'nutrition' in recipes.columns:
        nutrition_df = recipes['nutrition'].apply(eval).apply(pd.Series)
        nutrition_df.columns = ['calories', 'total_fat', 'sugar', 'sodium', 'protein', 'saturated_fat', 'carbs']
        
        # Add nutrition columns to recipes
        recipes['calories'] = nutrition_df['calories']
        recipes['protein'] = nutrition_df['protein']
        recipes['fat'] = nutrition_df['total_fat']
        recipes['carbs'] = nutrition_df['carbs']
        recipes['sugar'] = nutrition_df['sugar']
        recipes['sodium'] = nutrition_df['sodium']
    
    # Calculate Glycemic Load (GL)
    # GL = (carbs * GI) / 100
    # Using average GI estimate of 50 (medium GI)
    GI_ESTIMATE = 50
    
    if 'carbs' in recipes.columns:
        recipes['gl'] = (recipes['carbs'] * GI_ESTIMATE) / 100
    else:
        recipes['gl'] = 0
    
    # Clean ingredients (convert list to text)
    if 'ingredients' in recipes.columns:
        recipes['ingredients'] = recipes['ingredients'].apply(
            lambda x: ' '.join(eval(x)) if isinstance(x, str) else str(x)
        )
    
    # Clean steps (convert list to text)
    if 'steps' in recipes.columns:
        recipes['steps'] = recipes['steps'].apply(
            lambda x: ' '.join(eval(x)) if isinstance(x, str) and x != '[]' else ''
        )
    
    # Select relevant columns
    columns_to_keep = [
        'id', 'name', 'ingredients', 'calories', 'protein', 'fat', 
        'carbs', 'sugar', 'sodium', 'gl', 'steps'
    ]
    
    # Add image_url column (empty for now)
    recipes['image_url'] = ''
    columns_to_keep.append('image_url')
    
    recipes_final = recipes[columns_to_keep]
    
    # Remove any recipes with missing essential data
    recipes_final = recipes_final.dropna(subset=['id', 'name', 'ingredients'])
    
    # Fill missing numerical values with 0
    numerical_cols = ['calories', 'protein', 'fat', 'carbs', 'sugar', 'sodium', 'gl']
    recipes_final[numerical_cols] = recipes_final[numerical_cols].fillna(0)
    
    # Save processed recipes
    output_path = os.path.join('processed', output_file)
    os.makedirs('processed', exist_ok=True)
    recipes_final.to_csv(output_path, index=False)
    
    print(f"Processed recipes saved to {output_path}")
    print(f"Final recipe count: {len(recipes_final)}")
    
    return recipes_final


def preprocess_interactions(input_file='RAW_interactions.csv', output_file='ratings_processed.csv'):
    """
    Preprocess interactions/ratings data
    
    - Convert date to datetime
    - Calculate month_index for time-aware recommendations
    """
    print(f"Loading interactions from {input_file}...")
    
    # Read interactions
    interactions = pd.read_csv(input_file)
    
    print(f"Loaded {len(interactions)} interactions")
    
    # Convert date to datetime
    interactions['timestamp'] = pd.to_datetime(interactions['date'])
    
    # Calculate month_index (relative months since earliest rating)
    min_date = interactions['timestamp'].min()
    
    interactions['month_index'] = (
        (interactions['timestamp'].dt.year - min_date.year) * 12 + 
        (interactions['timestamp'].dt.month - min_date.month)
    ) + 1  # Start from 1
    
    # Rename columns for consistency
    interactions = interactions.rename(columns={
        'user_id': 'user_id',
        'recipe_id': 'recipe_id',
        'rating': 'rating'
    })
    
    # Select relevant columns
    columns_to_keep = ['user_id', 'recipe_id', 'rating', 'timestamp', 'month_index']
    interactions_final = interactions[columns_to_keep]
    
    # Remove any missing data
    interactions_final = interactions_final.dropna()
    
    # Ensure rating is between 1-5
    interactions_final = interactions_final[
        (interactions_final['rating'] >= 1) & 
        (interactions_final['rating'] <= 5)
    ]
    
    # Save processed interactions
    output_path = os.path.join('processed', output_file)
    os.makedirs('processed', exist_ok=True)
    interactions_final.to_csv(output_path, index=False)
    
    print(f"Processed interactions saved to {output_path}")
    print(f"Final interaction count: {len(interactions_final)}")
    print(f"Max month_index (TP): {interactions_final['month_index'].max()}")
    
    return interactions_final


def main():
    """
    Main preprocessing function
    """
    print("=" * 60)
    print("Food.com Dataset Preprocessing")
    print("=" * 60)
    
    # Check if raw files exist
    if not os.path.exists('RAW_recipes.csv'):
        print("ERROR: RAW_recipes.csv not found!")
        print("Please download the dataset from Kaggle:")
        print("https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions")
        return
    
    if not os.path.exists('RAW_interactions.csv'):
        print("ERROR: RAW_interactions.csv not found!")
        print("Please download the dataset from Kaggle:")
        print("https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions")
        return
    
    # Preprocess recipes
    print("\n" + "=" * 60)
    print("Step 1: Processing Recipes")
    print("=" * 60)
    recipes_df = preprocess_recipes()
    
    # Preprocess interactions
    print("\n" + "=" * 60)
    print("Step 2: Processing Interactions/Ratings")
    print("=" * 60)
    ratings_df = preprocess_interactions()
    
    # Summary
    print("\n" + "=" * 60)
    print("Preprocessing Complete!")
    print("=" * 60)
    print(f"Total Recipes: {len(recipes_df)}")
    print(f"Total Ratings: {len(ratings_df)}")
    print(f"Unique Users: {ratings_df['user_id'].nunique()}")
    print(f"Time Period Range: 1 to {ratings_df['month_index'].max()} months")
    print("\nNext Step: Run load_db.py to load data into SQLite database")


if __name__ == '__main__':
    main()
