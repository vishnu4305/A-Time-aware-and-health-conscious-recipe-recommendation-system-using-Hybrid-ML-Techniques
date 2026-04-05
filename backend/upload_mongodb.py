import pandas as pd
from pymongo import MongoClient
import ast

# Your MongoDB Connection String
MONGO_URI = "mongodb+srv://vishnu123:A.vishnu%40123@cluster0.1iu5btx.mongodb.net/?retryWrites=true&w=majority"

print("Connecting to MongoDB Atlas...")
client = MongoClient(MONGO_URI)
db = client['food_recommendation']

print("Reading RAW_recipes.csv... (This may take a minute)")
try:
    df = pd.read_csv('RAW_recipes.csv')
    
    records = []
    for i, row in df.iterrows():
        recipe = {
            '_id': int(row['id']),
            'name': str(row['name']),
            'ingredients': str(row['ingredients']),
            'minutes': int(row['minutes']),
            'n_ingredients': int(row['n_ingredients'])
        }
        
        # Parse nutrition array: [calories, total fat, sugar, sodium, protein, saturated fat, carbohydrates]
        try:
            nutrition = ast.literal_eval(row['nutrition'])
            recipe['calories'] = float(nutrition[0])
            recipe['total_fat'] = float(nutrition[1])
            recipe['sugar'] = float(nutrition[2])
            recipe['sodium'] = float(nutrition[3])
            recipe['protein'] = float(nutrition[4])
            recipe['saturated_fat'] = float(nutrition[5])
            recipe['carbohydrates'] = float(nutrition[6])
        except:
            continue
            
        records.append(recipe)
        
        # Insert in chunks of 5000 to avoid overloading RAM
        if len(records) >= 5000:
            print(f"Uploading recipes up to row {i}...")
            db.recipes.insert_many(records, ordered=False)
            records = []
            
    if records:
        db.recipes.insert_many(records, ordered=False)
        
    print("✅ Successfully uploaded all Kaggle recipes to MongoDB Atlas!")
except Exception as e:
    print("Error uploading to MongoDB:", e)