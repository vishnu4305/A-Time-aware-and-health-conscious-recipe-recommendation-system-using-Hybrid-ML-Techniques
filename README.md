# Time-Aware Health-Conscious Recipe Recommendation System

A multi-user web application that provides personalized recipe recommendations by balancing **taste preferences** with **health requirements** using machine learning.

## Key Features

- **Time-Aware Collaborative Filtering**: Recent ratings weighted more (based on Rostami et al., 2023)
- **Content-Based Filtering**: Semantic ingredient similarity using Sentence-Transformers
- **Health-Conscious Scoring**: WHO nutritional guidelines + obesity/diabetes management
- **Daily Meal Planner**: Organized breakfast, lunch, snacks, and dinner recommendations with calorie distribution
- **User Control**: Adjustable γ (taste vs health) and λ (time decay) sliders
- **Multi-User Support**: Personalized recommendations based on individual health profiles
- **Dual View Modes**: Regular recommendations list or structured daily meal plan

## Tech Stack

- **Frontend**: React.js with Bootstrap
- **Backend**: Python Flask
- **Database**: SQLite (file-based, no installation needed)
- **ML**: Sentence-Transformers, scikit-learn, Pandas, NumPy
- **Dataset**: Food.com Recipes (180k recipes, 700k ratings)

## Project Structure

```
Time-aware/
├── frontend/          # React application
├── backend/           # Flask API server
├── ml_models/         # Machine learning logic
│   ├── config/        # Meal type and distribution configs
│   ├── embeddings/    # Pre-computed recipe embeddings
│   ├── meal_classifier.py  # Meal type classification
│   └── meal_planner.py     # Calorie distribution logic
├── data/              # Dataset and processing scripts
├── database.sql       # SQLite schema
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- 8GB RAM minimum

**Note:** No database installation needed! SQLite comes with Python.

### 1. Initialize Database

```bash
# Create database tables
python init_database.py
```

This creates `food_db.sqlite` with empty tables.

### 2. Download Dataset

1. Download from Kaggle: https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
2. Extract `RAW_recipes.csv` and `RAW_interactions.csv` to `data/` folder

### 3. Backend Virtual Environment Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows CMD:
.\venv\Scripts\activate.bat

# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Process Data and Create Database

```bash
cd data

# Process the data (creates SQLite database automatically)
python preprocess.py
python load_db.py
```

This will create `food_db.sqlite` in the root directory - this file contains everything!

### 5. Run Backend

```bash
cd backend

# Make sure virtual environment is activated
# You should see (venv) in your terminal prompt

python app.py
```

Backend will run on `http://localhost:5000`

### 6. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend will run on `http://localhost:3000`

**Note:** The frontend connects to the backend at `http://localhost:5000` (configured in `frontend/.env`). If your backend runs on a different port, update `REACT_APP_API_URL` in `frontend/.env` and restart the frontend.

### Important Notes

- **Always activate the virtual environment** before running backend commands:
  ```powershell
  cd backend
  .\venv\Scripts\Activate.ps1
  ```
- You'll see `(venv)` in your prompt when activated
- To deactivate: `deactivate`
- Virtual environment folder (`venv/`) is already in `.gitignore`

## Sharing Your Project

### Super Easy Sharing (SQLite Advantage!)

To share your project with others:

1. **Copy the entire project folder** (including `food_db.sqlite`)
2. Other users only need to:
   - Install Python dependencies: `pip install -r requirements.txt`
   - Install npm packages: `npm install`
   - Run the app!

**No database setup required for other users!** The `food_db.sqlite` file contains all the data.

### For GitHub/Version Control

If pushing to GitHub:
- The database file (`food_db.sqlite`) can be shared via:
  - Git LFS (Large File Storage) if >100MB
  - Google Drive/Dropbox link in README
  - Or users download dataset and run preprocessing themselves

The database file will be approximately **500MB-1GB** depending on the dataset.

## How to Use

### Two Recommendation Modes

#### 1. Regular Recommendations
1. **Create Profile**: Enter name, age, height, weight, and health conditions
2. **Select Mode**: Choose "📋 Regular Recommendations"
3. **Adjust Preferences**:
   - **γ (Gamma)**: 0 = Pure Taste, 0.5 = Balanced, 1 = Pure Health
   - **λ (Lambda)**: 0.5-4.0 (higher = more recent preference focus)
4. **Get Recommendations**: Click button to see personalized recipes
5. **Rate Recipes**: Rate recipes 1-5 stars to improve future recommendations

#### 2. Daily Meal Plan (NEW!)
1. **Select Mode**: Choose "🍽️ Daily Meal Plan"
2. **Adjust Preferences**: Use γ and λ sliders same as regular mode
3. **Get Meal Plan**: Click button to get organized meal recommendations
4. **View by Meal Type**: 
   - 🌅 **Breakfast**    (25% of daily calories)
   - ☀️ **Lunch**        (35% of daily calories)
   - 🍎 **Snacks**       (10% of daily calories)
   - 🌙 **Dinner**       (30% of daily calories)
5. **Calorie Matching**: Each recipe shows how well it fits your meal's calorie target
6. **Rate and Improve**: Rate recipes to improve both regular and meal plan recommendations

## Algorithm Overview


### Final Score Formula
```
final_score = (1-γ) × preference + γ × health
preference = 0.6 × collaborative_filtering + 0.4 × content_based
```

### Time-Aware Collaborative Filtering
```
Time Weight (TW) = exp(-λ × (TP - t_ui)) + exp(-λ × (TP - t_uj))
```

### Health Scoring
- **WHO Guidelines**: Protein 10-15%, Fat 15-30%, Carbs 55-75%
- **Obesity**: Calorie deficit (500 kcal), penalty if recipe > 30% daily limit
- **Diabetes**: Penalty if sugar > 10g or Glycemic Load > 15

### Meal Classification System
- **Keyword Matching**: Recipe names analyzed for meal-specific terms
- **Ingredient Analysis**: Ingredients matched to meal type patterns
- **Calorie Range**: Breakfast (200-500), Lunch (400-700), Snacks (100-300), Dinner (500-900)
- **Macro Profiles**: Each meal type has specific protein/carb requirements
- **Scoring System**: Points assigned for each criterion, highest score determines meal type
- **Configuration-Driven**: All keywords and rules stored in JSON files (ml_models/config/)

## API Endpoints

### User Management
- `POST /user/create` - Create user profile
- `GET /user/<user_id>` - Get user profile
- `GET /user/by-name/<name>` - Get user by name

### Recommendations
- `POST /recommend` - Get regular recipe recommendations
- `POST /recommend/meal-plan` - Get organized daily meal plan (NEW!)

### Ratings
- `POST /rate` - Submit recipe rating
- `GET /user/<user_id>/ratings` - Get user's ratings

### Recipes
- `GET /recipes/<recipe_id>` - Get recipe details

### Health Check
- `GET /health` - API health status

## Development Timeline

- Week 1: Database setup + data preprocessing
- Week 2: Backend API + ML models (collaborative filtering, content-based)
- Week 3: Frontend development + health scoring
- Week 4: Meal classification + daily meal planner feature
- Week 5: Integration + testing + demo preparation

## Dataset Statistics

- **Total Recipes**: 231,636 recipes
- **Total Ratings**: 1,071,520 user ratings
- **Unique Users**: 196,098 users in dataset
- **Recipe ID Range**: 38 to 537,716
- **Database Size**: ~500MB (SQLite file)
- **Embeddings Size**: 231,636 × 384 dimensions (Sentence-Transformers)

## References

- Rostami et al. (2023) - Time-Aware Collaborative Filtering
- WHO Nutritional Guidelines
- Food.com Dataset (Kaggle)
- Sentence-Transformers (all-MiniLM-L6-v2)
- Mifflin-St Jeor Equation for BMR calculation

## Troubleshooting

### Common Issues

**1. PyTorch DLL Errors on Windows**
- Install Visual C++ Redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Or use PyTorch CPU version: `pip install torch==2.2.0`

**2. Virtual Environment Issues**
- Always use `backend/venv` not root `.venv`
- Activate: `cd backend; .\venv\Scripts\Activate.ps1`
- Verify: You should see `(venv)` in prompt

**3. No Recommendations Appearing**
- New users need to rate some recipes first (5-10 ratings recommended)
- Dataset ratings don't transfer to new user profiles
- Try adjusting γ (gamma) slider to different values

**4. Import Errors**
- Restart backend after code changes
- Check all dependencies installed: `pip list`
- Run from correct directory: `backend/` for app.py

**5. Meal Plan Shows Empty**
- Rate more recipes to improve classification
- Try regular recommendations first to build preference data
- Some recipes may not fit meal type categories well

## License

MIT License - College Project

## Authors

[Team-CAI-13]
[Vignan Lara ]
